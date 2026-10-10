"""
Apresentador (Presenter): PanelPresenter
Responsável por orquestrar a união entre os Modelos de Dados (ChurnDataset)
e as Visões modulares (templates HTML, CSS e JavaScript), compilando os relatórios
executivos finais com alta performance e sem duplicação de código.
"""

import os
import sys
from typing import List, Optional

# Adiciona a raiz do projeto ao path para imports limpos
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.models.churn_dataset import ChurnDataset


class PanelPresenter:
    def __init__(self, templates_dir: Optional[str] = None):
        self.templates_dir = templates_dir or os.path.join(ROOT_DIR, "templates", "churn_panel")
        self._css_cache: Optional[str] = None
        self._js_cache: Optional[str] = None
        self._layout_cache: Optional[str] = None

    def _read_file(self, filename: str) -> str:
        filepath = os.path.join(self.templates_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Template '{filename}' não encontrado em: {self.templates_dir}")
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    @property
    def styles_css(self) -> str:
        if self._css_cache is None:
            self._css_cache = self._read_file("styles.css")
        return self._css_cache

    @property
    def app_js(self) -> str:
        if self._js_cache is None:
            self._js_cache = self._read_file("app.js")
        return self._js_cache

    @property
    def layout_html(self) -> str:
        if self._layout_cache is None:
            self._layout_cache = self._read_file("layout.html")
        return self._layout_cache

    def compile_report(self, dataset: ChurnDataset, title_main: str, segment_key: str) -> str:
        """Monta o documento HTML completo compilando os templates com os dados."""
        html = self.layout_html

        # Injeção de componentes da View
        html = html.replace("{{STYLES}}", self.styles_css)
        html = html.replace("{{APP_JS}}", self.app_js)

        # Injeção de variáveis de cabeçalho
        html = html.replace("{{TITLE_MAIN}}", title_main)
        html = html.replace("{{SEGMENT_KEY}}", segment_key)

        # Injeção do Modelo de Dados serializado em JSON
        html = html.replace("{{RAW_DATA_JSON}}", dataset.to_json_string())

        return html

    def generate_report(
        self,
        data_path: str,
        title_main: str,
        title_sub: str,
        segment_key: str,
        output_html_path: str,
        standalone_path: Optional[str] = None,
        extra_output_paths: Optional[List[str]] = None,
    ) -> None:
        """Carrega os dados via Model, compila o HTML e grava em todos os caminhos de saída."""
        dataset = ChurnDataset(data_path)
        compiled_html = self.compile_report(dataset, title_main, segment_key)

        # 1. Arquivo principal
        os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(compiled_html)

        # 2. Arquivo standalone na pasta do módulo
        if standalone_path:
            os.makedirs(os.path.dirname(standalone_path), exist_ok=True)
            with open(standalone_path, "w", encoding="utf-8") as f:
                f.write(compiled_html)

        # 3. Arquivos na raiz do projeto (para compatibilidade legada)
        extra_paths = extra_output_paths or []
        for ep in extra_paths:
            os.makedirs(os.path.dirname(ep) if os.path.dirname(ep) else ".", exist_ok=True)
            with open(ep, "w", encoding="utf-8") as f:
                f.write(compiled_html)

        print(f"✅ [Presenter] Relatório gerado com sucesso: {output_html_path}")

    def generate_all_reports(self) -> None:
        """Executa a compilação de todos os painéis da Regional Norte (Total e PME)."""
        print("\n🚀 [Presenter] Iniciando compilação modular dos relatórios de Churn...\n")

        # 1. Banda Larga Total
        self.generate_report(
            data_path=os.path.join(ROOT_DIR, "public", "churn-bl-total", "data.json"),
            title_main="Painel Churn Banda Larga Total",
            title_sub="Acompanhamento Executivo de Churn Horizontal",
            segment_key="Banda Larga Total",
            output_html_path=os.path.join(ROOT_DIR, "public", "churn-bl-total", "index.html"),
            standalone_path=os.path.join(
                ROOT_DIR, "public", "churn-bl-total", "Painel_Churn_Banda_Larga_Total.html"
            ),
            extra_output_paths=[
                os.path.join(ROOT_DIR, "Painel_Churn_Banda_Larga_Total.html"),
                os.path.join(ROOT_DIR, "Painel_Churn_Total.html"),
            ],
        )

        # 2. Banda Larga PME
        self.generate_report(
            data_path=os.path.join(ROOT_DIR, "public", "churn-bl-pme", "data.json"),
            title_main="Painel Churn Banda Larga PME",
            title_sub="Acompanhamento Executivo de Churn Horizontal PME",
            segment_key="Banda Larga PME",
            output_html_path=os.path.join(ROOT_DIR, "public", "churn-bl-pme", "index.html"),
            standalone_path=os.path.join(
                ROOT_DIR, "public", "churn-bl-pme", "Painel_Churn_Banda_Larga_PME.html"
            ),
            extra_output_paths=[
                os.path.join(ROOT_DIR, "Painel_Churn_Banda_Larga_PME.html"),
                os.path.join(ROOT_DIR, "Painel_Churn_PME.html"),
            ],
        )

        print("\n🎉 Todos os relatórios foram gerados e sincronizados com sucesso!")
