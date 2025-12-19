from pathlib import Path
from typing import List
from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from app.config import settings

class DocumentLoader:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, 
            chunk_overlap=200,
            add_start_index=True,
        )
        print("Initializing Docling Converter with EasyOCR (Thai+English) + GPU...")
        
        # Configure EasyOCR for Thai and English with GPU
        ocr_options = EasyOcrOptions(lang=["th", "en"], use_gpu=True)
        
        # Enable GPU acceleration for the pipeline
        accelerator_options = AcceleratorOptions(device="cuda")
        
        pipeline_options = PdfPipelineOptions(
            ocr_options=ocr_options,
            accelerator_options=accelerator_options
        )
        
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

    def load_documents(self) -> List[LCDocument]:
        dataset_path = Path(settings.DATASET_PATH)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset directory not found: {dataset_path}")

        documents = []
        files = list(dataset_path.glob("*.pdf"))
        
        print(f"Found {len(files)} PDF files in {dataset_path}")

        for file_path in files:
            print(f"Processing {file_path.name} with Docling...")
            try:
                result = self.converter.convert(file_path)
                doc = result.document
                
                # Extract text page by page with correct page numbers
                for page_no, page in doc.pages.items():
                    # Get text content for this page by filtering document items
                    page_texts = []
                    for item, _level in doc.iterate_items():
                        # Check if item has prov (provenance) with page info
                        if hasattr(item, 'prov') and item.prov:
                            for prov in item.prov:
                                if hasattr(prov, 'page_no') and prov.page_no == page_no:
                                    if hasattr(item, 'text') and item.text:
                                        page_texts.append(item.text)
                                    break
                    
                    page_content = "\n".join(page_texts)
                    
                    if page_content.strip():
                        lc_doc = LCDocument(
                            page_content=page_content,
                            metadata={
                                "source": file_path.name,
                                "page": page_no
                            }
                        )
                        documents.append(lc_doc)
                
                print(f"  Extracted {len([d for d in documents if d.metadata['source'] == file_path.name])} pages")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        chunked_docs = self.text_splitter.split_documents(documents)
        print(f"Split {len(documents)} pages into {len(chunked_docs)} chunks.")
        
        return chunked_docs


