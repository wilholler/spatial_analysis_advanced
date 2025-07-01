# -*- coding: utf-8 -*-
"""
Plugin de Análise de Autocorrelação Espacial para QGIS
Implementa I de Moran e LISA com visualização automática

Este arquivo é o ponto de entrada do plugin. O QGIS chama a função
classFactory automaticamente quando o plugin é carregado.
"""

def classFactory(iface):
    """
    Função obrigatória chamada pelo QGIS para carregar o plugin.
    
    Esta é uma convenção do QGIS - todo plugin deve ter uma função
    chamada exatamente 'classFactory' que retorna uma instância
    da classe principal do plugin.
    
    Args:
        iface: QgisInterface - interface que permite ao plugin
               interagir com a aplicação principal do QGIS
               
    Returns:
        Instância da classe principal do plugin
    """
    # Importar a classe principal do plugin
    # O ponto antes do nome indica importação relativa (mesmo diretório)
    from .spatial_analysis import SpatialAnalysisPlugin
    
    # Retornar uma instância do plugin, passando a interface do QGIS
    return SpatialAnalysisPlugin(iface)