"""
Ponto de Entrada (Entrypoint) para Geração dos Relatórios de Churn do Pephub.
Refatorado segundo o padrão arquitetural MVP (Model-View-Presenter):
- Model: src.models.churn_dataset.ChurnDataset (dados e validação)
- View: templates/churn_panel/ (styles.css, layout.html, app.js desacoplados)
- Presenter: src.presenters.panel_presenter.PanelPresenter (orquestração e compilação)
"""

import os
import sys

# Garante acesso aos módulos em src
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.presenters.panel_presenter import PanelPresenter

_presenter = PanelPresenter()


def generate_panel_html(
    data_path: str,
    title_main: str,
    title_sub: str,
    segment_key: str,
    output_html_path: str,
    standalone_path: str = None,
    extra_output_paths: list = None,
):
    """Mantido para compatibilidade total com chamadas de automação existentes."""
    _presenter.generate_report(
        data_path=data_path,
        title_main=title_main,
        title_sub=title_sub,
        segment_key=segment_key,
        output_html_path=output_html_path,
        standalone_path=standalone_path,
        extra_output_paths=extra_output_paths,
    )


def run_all_generations():
    """Compila todos os relatórios da Regional Norte (Banda Larga Total e PME)."""
    _presenter.generate_all_reports()


if __name__ == "__main__":
    run_all_generations()
