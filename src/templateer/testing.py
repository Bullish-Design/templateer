"""Testing utilities and fixtures for templateer."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from .core import TemplateModel
from .generator import autogen_models
from .settings import get_settings

if TYPE_CHECKING:
    try:
        from pydantree import Parser
        from pydantree import ParsedDocument
        from tree_sitter_languages import get_language
    except ImportError:
        pass


class TemplateTestHelper:
    """Helper for testing template generation."""
    
    def __init__(self, temp_dir: Path) -> None:
        self.temp_dir = temp_dir
        self.settings = None
    
    def setup_test_environment(self) -> None:
        """Set up temporary testing directories."""
        temp_models = self.temp_dir / "models"
        temp_output = self.temp_dir / "generated"
        
        os.environ["MODEL_DIR"] = str(temp_models)
        os.environ["TEMPLATE_OUTPUT_DIR"] = str(temp_output)
        
        # Force settings reload
        self.settings = get_settings()
        
        # Generate stubs and instantiate templates
        autogen_models()
        self._instantiate_all_templates()
    
    def _instantiate_all_templates(self) -> None:
        """Load and instantiate all template models."""
        sys.path.insert(0, str(self.settings.model_dir))
        
        for stub in self.settings.model_dir.glob("*_model.py"):
            spec = importlib.util.spec_from_file_location(
                stub.stem, stub
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            
            tmpl_cls = next(
                c for c in mod.__dict__.values()
                if (isinstance(c, type) 
                    and issubclass(c, TemplateModel) 
                    and c is not TemplateModel)
            )
            
            # Generate output files
            tmpl_cls().generate()


@pytest.fixture(scope="session")
def template_test_helper(tmp_path_factory):
    """Pytest fixture for template testing."""
    temp_dir = tmp_path_factory.mktemp("templateer_test")
    helper = TemplateTestHelper(temp_dir)
    helper.setup_test_environment()
    yield helper


def test_generated_syntax(template_test_helper):
    """Test that generated Python files have valid syntax."""
    try:
        from pydantree import Parser
        from pydantree import ParsedDocument
        from tree_sitter_languages import get_language
    except ImportError:
        pytest.skip("tree-sitter dependencies not available")
    
    py_language = get_language("python")
    ts_parser = Parser(py_language)
    
    output_dir = Path(os.environ["TEMPLATE_OUTPUT_DIR"])
    
    for py_file in output_dir.glob("*.py"):
        text = py_file.read_text()
        doc = ParsedDocument(text=text, parser=ts_parser)
        assert doc.root.type_name == "module"


def test_generated_imports(template_test_helper):
    """Test that generated files can be imported."""
    output_dir = Path(os.environ["TEMPLATE_OUTPUT_DIR"])
    
    for py_file in output_dir.glob("*.py"):
        spec = importlib.util.spec_from_file_location(
            py_file.stem, py_file
        )
        mod = importlib.util.module_from_spec(spec)
        
        # Should not raise ImportError
        spec.loader.exec_module(mod)
