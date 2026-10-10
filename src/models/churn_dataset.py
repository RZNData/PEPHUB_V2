"""
Modelo de Dados (Model): ChurnDataset
Responsável pelo carregamento, validação e integridade dos datasets de Churn
(Banda Larga Total e PME) a partir de arquivos JSON estruturados.
"""

import json
import os
from typing import Dict, Any, List, Optional


class ChurnDataset:
    REQUIRED_ROOT_KEYS = ["segmento", "mes_referencia", "modes"]

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Carrega e valida a integridade do arquivo JSON de dados."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Arquivo de dados não encontrado: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self._validate()

    def _validate(self) -> None:
        """Garante que a estrutura esperada pelo painel está presente."""
        for key in self.REQUIRED_ROOT_KEYS:
            if key not in self.data:
                raise ValueError(
                    f"Erro de integridade no dataset '{self.file_path}': chave obrigatória '{key}' ausente."
                )

        modes = self.data.get("modes", {})
        if "TOTAL" not in modes:
            raise ValueError(
                f"Erro de integridade no dataset '{self.file_path}': modo 'TOTAL' não encontrado em 'modes'."
            )

    @property
    def segmento(self) -> str:
        return self.data.get("segmento", "Banda Larga")

    @property
    def mes_referencia(self) -> str:
        return self.data.get("mes_referencia", "Setembro / 2026")

    @property
    def data_posicao(self) -> str:
        return self.data.get("data_posicao", "Fechamento S4")

    @property
    def modes(self) -> List[str]:
        return list(self.data.get("modes", {}).keys())

    def get_cities(self, mode: str = "TOTAL") -> List[Dict[str, Any]]:
        mode_upper = mode.upper()
        return self.data.get("modes", {}).get(mode_upper, {}).get("cities", [])

    def to_json_string(self) -> str:
        """Serializa o dataset completo para injeção limpa no bundle HTML/JS."""
        return json.dumps(self.data, ensure_ascii=False)
