# -*- coding: utf-8 -*-
"""
Plugin QGIS para Análise de Autocorrelação Espacial - V 1.0.0
Implementa I de Moran e LISA com visualização automática e tratamento para polígonos com dados numéricos.

Autor: Wilson Holler
Versão: 1.0.0
Data: 07/01/2025

Este plugin oferece:
- Análise I de Moran Global com testes de permutação
- Análise LISA (Local Indicators of Spatial Association)
- Tratamento especializado para dados de contagem (Poisson)
- Visualização automática com mapas temáticos
- Interface educativa e intuitiva
- Salvamento de resultados como arquivo permanente (shp)
"""

import os
import sys

# Verifica e importa dependências necessárias
try:
    import numpy as np
    import scipy.spatial.distance as distance
    from scipy import stats
    from scipy.spatial import Delaunay
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from qgis.PyQt.QtCore import QVariant, Qt, QTimer
from qgis.PyQt.QtWidgets import (QAction, QDialog, QVBoxLayout, QHBoxLayout, 
                                QPushButton, QComboBox, QLabel, QMessageBox, 
                                QProgressBar, QCheckBox, QSpinBox, QDoubleSpinBox,
                                QGroupBox, QGridLayout, QTextEdit, QApplication)
from qgis.PyQt.QtGui import QIcon, QColor

from qgis.core import (QgsProject, QgsVectorLayer, QgsField, QgsFeature, 
                       QgsGeometry, QgsPointXY, QgsProcessingUtils, 
                       QgsWkbTypes, QgsApplication, QgsMessageLog,
                       QgsSymbol, QgsRendererRange, QgsGraduatedSymbolRenderer,
                       QgsCategorizedSymbolRenderer, QgsRendererCategory,
                       QgsSimpleFillSymbolLayer, QgsRuleBasedRenderer,
                       QgsFillSymbol, QgsColorRamp, QgsGradientColorRamp,
                       QgsGradientStop, QgsSymbolLayer, QgsMarkerSymbol,
                       QgsMapLayerProxyModel, QgsVectorFileWriter)

# Importa Qgis com fallback para compatibilidade
try:
    from qgis.core import Qgis
    QGIS_LOG_AVAILABLE = True
except ImportError:
    QGIS_LOG_AVAILABLE = False

from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox
from qgis.utils import iface

# Função helper para garantir compatibilidade com logging
def safe_log_message(message, tag="Spatial Analysis", level="info"):
    """
    Função para log que funciona em diferentes versões do QGIS
    """
    if not QGIS_LOG_AVAILABLE:
        # Se Qgis não está disponível, usa print simples
        print(f"[{tag}] {message}")
        return
        
    try:
        # Tenta usar as constantes mais recentes do QGIS
        if level.lower() == "warning":
            log_level = Qgis.Warning
        elif level.lower() == "critical":
            log_level = Qgis.Critical
        else:
            log_level = Qgis.Info
        
        QgsMessageLog.logMessage(message, tag, log_level)
    except:
        try:
            # Fallback para valores numéricos (compatibilidade com versões antigas)
            if level.lower() == "warning":
                log_level = 1
            elif level.lower() == "critical":  
                log_level = 2
            else:
                log_level = 0
                
            QgsMessageLog.logMessage(message, tag, log_level)
        except:
            # Último fallback - apenas print se tudo falhar
            print(f"[{tag}] {message}")


class SpatialAnalysisPlugin:
    """Plugin principal para análise espacial avançada"""
    
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
    def initGui(self):
        """Inicializa a interface gráfica do plugin"""
        # Verifica dependências antes de adicionar à interface
        if not SCIPY_AVAILABLE:
            QMessageBox.warning(
                None, 
                "Dependências Ausentes", 
                "O plugin requer a biblioteca SciPy. Por favor, instale usando:\n"
                "pip install scipy\n\n"
                "No Windows com OSGeo4W, use:\n"
                "py3_env.bat && python -m pip install scipy"
            )
            return
        
        # Cria ação para o menu com ícone
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        if os.path.exists(icon_path):
            self.action = QAction(QIcon(icon_path), "Análise Espacial Avançada", self.iface.mainWindow())
        else:
            self.action = QAction("Análise Espacial Avançada", self.iface.mainWindow())
        
        self.action.triggered.connect(self.run)
        
        # Adiciona ao menu e toolbar
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu("Análise Espacial", self.action)
        
    def unload(self):
        """Remove o plugin da interface"""
        self.iface.removePluginVectorMenu("Análise Espacial", self.action)
        self.iface.removeToolBarIcon(self.action)
        
    def run(self):
        """Executa o plugin"""
        dialog = SpatialAnalysisDialog()
        dialog.exec_()


class SpatialAnalysisDialog(QDialog):
    """Dialog principal para configurar a análise espacial"""
    
    def __init__(self):
        super().__init__()
        self.analysis_worker = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_progress)
        self.setupUi()
        
    def setupUi(self):
        """Configura a interface do usuário de forma intuitiva e didática"""
        self.setWindowTitle("Análise de Autocorrelação Espacial - I de Moran e LISA")
        self.setFixedSize(500, 650)
        
        layout = QVBoxLayout()
        
        # Seção 1: Seleção de dados
        data_group = QGroupBox("1. Configuração dos Dados")
        data_layout = QGridLayout()
        
        data_layout.addWidget(QLabel("Camada vetorial (Polígonos):"), 0, 0)
        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        data_layout.addWidget(self.layer_combo, 0, 1)
        
        data_layout.addWidget(QLabel("Campo para análise:"), 1, 0)
        self.field_combo = QgsFieldComboBox()
        self.field_combo.setLayer(self.layer_combo.currentLayer())
        data_layout.addWidget(self.field_combo, 1, 1)
        
        # Conecta mudança de camada com atualização de campos de forma segura
        try:
            self.layer_combo.layerChanged.connect(self.field_combo.setLayer)
        except Exception as e:
            safe_log_message(f"Erro ao conectar signals: {str(e)}", "Spatial Analysis", "warning")
        
        data_layout.addWidget(QLabel("Tipo de dados:"), 2, 0)
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["Contagem (Poisson)", "Contínuo (Gaussiano)", "Taxa/Proporção"])
        data_layout.addWidget(self.data_type_combo, 2, 1)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # Seção 2: Configuração de vizinhança
        neighbor_group = QGroupBox("2. Definição de Vizinhança Espacial")
        neighbor_layout = QGridLayout()
        
        neighbor_layout.addWidget(QLabel("Critério de vizinhança:"), 0, 0)
        self.neighbor_combo = QComboBox()
        self.neighbor_combo.addItems(["Queen (Adjacência completa)", 
                                     "Rook (Adjacência lateral)", 
                                     "K-vizinhos mais próximos", 
                                     "Distância fixa (raio)"])
        neighbor_layout.addWidget(self.neighbor_combo, 0, 1)
        
        # Parâmetros específicos para diferentes tipos de vizinhança
        neighbor_layout.addWidget(QLabel("Número de vizinhos (K):"), 1, 0)
        self.k_neighbors = QSpinBox()
        self.k_neighbors.setRange(1, 50)
        self.k_neighbors.setValue(8)
        neighbor_layout.addWidget(self.k_neighbors, 1, 1)
        
        neighbor_layout.addWidget(QLabel("Raio de distância:"), 2, 0)
        self.distance_radius = QDoubleSpinBox()
        self.distance_radius.setRange(0.1, 999999.0)
        self.distance_radius.setValue(1000.0)
        neighbor_layout.addWidget(self.distance_radius, 2, 1)
        
        # Conectar mudança no tipo de vizinhança para ativar/desativar controles
        try:
            self.neighbor_combo.currentTextChanged.connect(self.update_neighbor_controls)
        except Exception as e:
            safe_log_message(f"Erro ao conectar signal de vizinhança: {str(e)}", "Spatial Analysis", "warning")
        
        neighbor_group.setLayout(neighbor_layout)
        layout.addWidget(neighbor_group)
        
        # Seção 3: Tipo de análise
        analysis_group = QGroupBox("3. Métodos de Análise")
        analysis_layout = QVBoxLayout()
        
        self.global_moran_check = QCheckBox("I de Moran Global (padrão geral de autocorrelação)")
        self.global_moran_check.setChecked(True)
        analysis_layout.addWidget(self.global_moran_check)
        
        self.lisa_check = QCheckBox("LISA - Indicadores Locais (hotspots e coldspots)")
        self.lisa_check.setChecked(True)
        analysis_layout.addWidget(self.lisa_check)
        
        self.create_maps_check = QCheckBox("Gerar mapas temáticos automaticamente")
        self.create_maps_check.setChecked(True)
        analysis_layout.addWidget(self.create_maps_check)
        
        self.save_file_check = QCheckBox("Salvar resultado como arquivo permanente (Shapefile)")
        self.save_file_check.setChecked(False)
        analysis_layout.addWidget(self.save_file_check)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Seção 4: Configurações estatísticas
        stats_group = QGroupBox("4. Configurações Estatísticas")
        stats_layout = QGridLayout()
        
        stats_layout.addWidget(QLabel("Nível de significância:"), 0, 0)
        self.significance_combo = QComboBox()
        self.significance_combo.addItems(["0.05 (95% confiança)", "0.01 (99% confiança)", "0.001 (99.9% confiança)"])
        stats_layout.addWidget(self.significance_combo, 0, 1)
        
        stats_layout.addWidget(QLabel("Número de permutações:"), 1, 0)
        self.permutations_spin = QSpinBox()
        self.permutations_spin.setRange(99, 9999)
        self.permutations_spin.setValue(999)
        stats_layout.addWidget(self.permutations_spin, 1, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Executar Análise Completa")
        self.run_button.clicked.connect(self.run_analysis)
        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Configurações iniciais
        self.update_neighbor_controls()
    
    def update_neighbor_controls(self):
        """Atualiza os controles baseado no tipo de vizinhança selecionado"""
        neighbor_type = self.neighbor_combo.currentText()
        
        # Habilitar/desabilitar controles baseado na seleção
        self.k_neighbors.setEnabled("K-vizinhos" in neighbor_type)
        self.distance_radius.setEnabled("Distância fixa" in neighbor_type)
    
    def run_analysis(self):
        """Executa a análise espacial configurada pelo usuário"""
        # Verificar se SciPy está disponível
        if not SCIPY_AVAILABLE:
            QMessageBox.critical(self, "Dependências Ausentes", 
                               "O plugin requer a biblioteca SciPy.\n\n"
                               "Para instalar:\n"
                               "• Windows (OSGeo4W): Abra o OSGeo4W Shell como administrador e execute:\n"
                               "  python -m pip install scipy\n\n"
                               "• Outras instalações: pip install scipy\n\n"
                               "Reinicie o QGIS após a instalação.")
            return
        
        layer = self.layer_combo.currentLayer()
        field_name = self.field_combo.currentField()
        
        # Verificações de validação melhoradas
        if not layer:
            QMessageBox.warning(self, "Erro", 
                              "Nenhuma camada vetorial foi selecionada.\n\n"
                              "Por favor, carregue uma camada vetorial no projeto e tente novamente.")
            return
            
        if not field_name:
            QMessageBox.warning(self, "Erro", 
                              "Nenhum campo foi selecionado para análise.\n\n"
                              "Certifique-se de que a camada possui campos numéricos.")
            return
        
        # Verificar se a camada possui features
        if layer.featureCount() == 0:
            QMessageBox.warning(self, "Erro", 
                              "A camada selecionada não possui feições.\n\n"
                              "Certifique-se de que a camada contém dados geográficos.")
            return
        
        # Verificar se há pelo menos 3 features para análise espacial
        if layer.featureCount() < 3:
            QMessageBox.warning(self, "Erro", 
                              "A análise espacial requer pelo menos 3 feições.\n\n"
                              f"A camada atual possui apenas {layer.featureCount()} feição(ões).")
            return
        
        if not self.global_moran_check.isChecked() and not self.lisa_check.isChecked():
            QMessageBox.warning(self, "Erro", 
                              "Selecione pelo menos um tipo de análise.\n\n"
                              "Marque 'I de Moran Global' ou 'LISA' (ou ambos).")
            return
        
        # Configurar parâmetros para a análise
        analysis_params = {
            'layer': layer,
            'field_name': field_name,
            'data_type': self.data_type_combo.currentText(),
            'neighbor_type': self.neighbor_combo.currentText(),
            'k_neighbors': self.k_neighbors.value(),
            'distance_radius': self.distance_radius.value(),
            'run_global': self.global_moran_check.isChecked(),
            'run_lisa': self.lisa_check.isChecked(),
            'create_maps': self.create_maps_check.isChecked(),
            'save_file': self.save_file_check.isChecked(),
            'significance_level': float(self.significance_combo.currentText().split()[0]),
            'permutations': self.permutations_spin.value()
        }
        
        # Criar worker e executar análise em modo síncrono simplificado
        self.analysis_worker = SpatialAnalysisWorker(analysis_params)
        
        self.progress_bar.setVisible(True)
        self.run_button.setEnabled(False)
        self.status_label.setText("Iniciando análise...")
        
        # Usar timer para executar análise sem bloquear interface
        self.timer.start(100)  # Verificar progresso a cada 100ms
        
        # Executar análise em thread principal (simplificado)
        try:
            QApplication.processEvents()  # Manter interface responsiva
            results = self.analysis_worker.run_analysis()
            self.analysis_finished(results)
        except Exception as e:
            self.analysis_error(str(e))
    
    def check_progress(self):
        """Verifica o progresso da análise"""
        if self.analysis_worker and hasattr(self.analysis_worker, 'current_progress'):
            self.progress_bar.setValue(self.analysis_worker.current_progress)
            if hasattr(self.analysis_worker, 'current_status'):
                self.status_label.setText(self.analysis_worker.current_status)
            QApplication.processEvents()
    
    def analysis_finished(self, results):
        """Processa os resultados quando a análise termina com sucesso"""
        self.timer.stop()
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.status_label.setText("Análise concluída com sucesso!")
        
        # Mostrar resultados em dialog especializado
        result_dialog = AdvancedResultsDialog(results)
        result_dialog.exec_()
    
    def analysis_error(self, error_msg):
        """Trata erros que podem ocorrer durante a análise"""
        self.timer.stop()
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.status_label.setText("Erro na análise")
        QMessageBox.critical(self, "Erro na Análise", 
                           f"Ocorreu um erro durante a análise:\n\n{error_msg}")


class SpatialAnalysisWorker:
    """Worker simplificado para executar análise espacial"""
    
    def __init__(self, params):
        self.params = params
        self.current_progress = 0
        self.current_status = "Inicializando..."
        
    def update_progress(self, value, status=""):
        """Atualiza progresso e status"""
        self.current_progress = value
        if status:
            self.current_status = status
        QApplication.processEvents()
        
    def run_analysis(self):
        """Executa toda a análise espacial com tratamento específico para dados de contagem"""
        # Fase 1: Extração e validação dos dados
        self.update_progress(5, "Extraindo dados da camada...")
        features, values, coordinates = self.extract_and_validate_data()
        
        if len(values) < 3:
            raise Exception("Número insuficiente de observações válidas (mínimo 3 necessárias).")
        
        # Fase 2: Construção da matriz de pesos espaciais
        self.update_progress(20, "Construindo matriz de pesos espaciais...")
        W = self.build_spatial_weights_matrix(coordinates)
        
        # Fase 3: Preparação dos dados baseada no tipo
        self.update_progress(35, "Preparando dados para análise...")
        processed_values = self.prepare_data_by_type(values)
        
        # Fase 4: Análises estatísticas
        results = {'original_values': values, 'processed_values': processed_values}
        
        if self.params['run_global']:
            self.update_progress(50, "Calculando I de Moran global...")
            results['moran'] = self.calculate_advanced_moran_i(processed_values, W)
        
        if self.params['run_lisa']:
            self.update_progress(70, "Calculando indicadores LISA...")
            results['lisa'] = self.calculate_advanced_lisa(processed_values, W)
            
            # Criar camada com resultados LISA
            self.update_progress(85, "Criando camada de resultados...")
            lisa_layer = self.create_lisa_layer(features, results['lisa'])
            results['lisa_layer'] = lisa_layer
            
            # Salvar arquivo permanente se solicitado
            if self.params['save_file']:
                self.update_progress(90, "Salvando arquivo permanente...")
                saved_file = self.save_layer_to_file(lisa_layer)
                if saved_file:
                    results['saved_file'] = saved_file
                    safe_log_message(f"Arquivo salvo em: {saved_file}", "Spatial Analysis", "info")
            
            # Criar visualização automática se solicitado
            if self.params['create_maps']:
                self.update_progress(95, "Aplicando visualização automática...")
                self.create_automatic_visualization(lisa_layer, results['lisa'])
        
        self.update_progress(100, "Análise concluída!")
        return results
    
    def extract_and_validate_data(self):
        """Extrai e valida dados da camada vetorial com verificações robustas"""
        features = []
        values = []
        coordinates = []
        invalid_count = 0
        
        field_name = self.params['field_name']
        layer = self.params['layer']
        
        for feature in layer.getFeatures():
            # Verificar geometria válida
            geom = feature.geometry()
            if not geom or geom.isEmpty():
                invalid_count += 1
                continue
                
            # Verificar valor do campo
            field_value = feature[field_name]
            if field_value is None or field_value == '' or str(field_value).lower() in ['null', 'na', 'n/a', 'nan']:
                invalid_count += 1
                continue
                
            try:
                value = float(field_value)
                
                # Verificar se é um número válido (não infinito, não NaN)
                if not np.isfinite(value):
                    invalid_count += 1
                    continue
                
                # Para dados de contagem, verificar se são não-negativos
                if self.params['data_type'].startswith("Contagem") and value < 0:
                    invalid_count += 1
                    continue
                    
                values.append(value)
                features.append(feature)
                
                # Obter coordenadas do centroide
                if geom.type() == QgsWkbTypes.PointGeometry:
                    point = geom.asPoint()
                    coordinates.append([point.x(), point.y()])
                else:
                    centroid = geom.centroid().asPoint()
                    coordinates.append([centroid.x(), centroid.y()])
                    
            except (ValueError, TypeError):
                invalid_count += 1
                continue
        
        # Log de informações sobre dados inválidos
        if invalid_count > 0:
            safe_log_message(
                f"Foram ignoradas {invalid_count} feições com dados inválidos ou ausentes.", 
                "Spatial Analysis", 
                "info"
            )
        
        if len(values) == 0:
            raise Exception(f"Nenhum valor numérico válido encontrado no campo '{field_name}'.\n"
                          "Verifique se o campo contém dados numéricos válidos.")
        
        return features, np.array(values), np.array(coordinates)
    
    def build_spatial_weights_matrix(self, coordinates):
        """Constrói matriz de pesos espaciais baseada no critério selecionado"""
        n = len(coordinates)
        W = np.zeros((n, n))
        
        neighbor_type = self.params['neighbor_type']
        
        if "Queen" in neighbor_type:
            # Usar triangulação de Delaunay para definir adjacência Queen
            if n >= 3:  # Mínimo necessário para triangulação
                try:
                    tri = Delaunay(coordinates)
                    for simplex in tri.simplices:
                        for i in range(len(simplex)):
                            for j in range(i+1, len(simplex)):
                                W[simplex[i], simplex[j]] = 1
                                W[simplex[j], simplex[i]] = 1
                except Exception as e:
                    # Se triangulação falhar, usar K-nearest neighbors como fallback
                    safe_log_message(
                        f"Triangulação falhou, usando K-vizinhos como alternativa: {str(e)}", 
                        "Spatial Analysis", 
                        "warning"
                    )
                    # Fallback para K-nearest neighbors
                    k = min(4, n-1)
                    distances = distance.cdist(coordinates, coordinates)
                    for i in range(n):
                        nearest = np.argsort(distances[i])[1:k+1]
                        W[i, nearest] = 1
                        
        elif "Rook" in neighbor_type:
            # Implementação simplificada de Rook usando distância mínima
            distances = distance.cdist(coordinates, coordinates)
            # Encontrar distância mínima não-zero
            min_dist = np.min(distances[distances > 0])
            threshold = min_dist * 1.1  # Margem de 10%
            W = (distances <= threshold) & (distances > 0)
            W = W.astype(float)
            
        elif "K-vizinhos" in neighbor_type:
            # K-nearest neighbors
            k = min(self.params['k_neighbors'], n-1)
            distances = distance.cdist(coordinates, coordinates)
            for i in range(n):
                nearest = np.argsort(distances[i])[1:k+1]  # Excluir o próprio ponto
                W[i, nearest] = 1
                
        elif "Distância fixa" in neighbor_type:
            # Distância fixa (raio)
            radius = self.params['distance_radius']
            distances = distance.cdist(coordinates, coordinates)
            W = (distances <= radius) & (distances > 0)
            W = W.astype(float)
        
        # Normalização linha por linha (row standardization)
        row_sums = W.sum(axis=1)
        for i in range(n):
            if row_sums[i] > 0:
                W[i] = W[i] / row_sums[i]
        
        return W
    
    def prepare_data_by_type(self, values):
        """Prepara os dados baseado no tipo especificado (contagem vs contínuo)"""
        data_type = self.params['data_type']
        
        if "Contagem" in data_type:
            # Para dados de contagem, aplicar transformação estabilizadora de variância
            # Usando transformação de Freeman-Tukey para dados de Poisson
            processed = np.sqrt(values) + np.sqrt(values + 1)
        elif "Taxa" in data_type:
            # Para taxas/proporções, usar transformação logit ou arcsin
            # Aqui usamos arcsin para proporções
            processed = np.arcsin(np.sqrt(np.clip(values, 0, 1)))
        else:
            # Para dados contínuos, usar os valores originais
            processed = values.copy()
        
        return processed
    
    def calculate_advanced_moran_i(self, values, W):
        """Calcula I de Moran com testes de permutação para dados de contagem"""
        n = len(values)
        
        # Centralizar os valores
        y = values - np.mean(values)
        
        # Calcular I de Moran observado
        numerator = 0
        denominator = np.sum(y**2)
        S0 = np.sum(W)  # Soma de todos os pesos
        
        for i in range(n):
            for j in range(n):
                numerator += W[i,j] * y[i] * y[j]
        
        I_observed = (n / S0) * (numerator / denominator)
        
        # Valor esperado
        E_I = -1 / (n - 1)
        
        # Teste de permutação simplificado (menos permutações para rapidez)
        permutations = min(self.params['permutations'], 199)  # Limitar para performance
        I_permuted = []
        valid_permutations = 0
        
        for perm_i in range(permutations):
            try:
                # Permutação aleatória dos valores
                y_perm = np.random.permutation(y)
                
                # Calcular I para a permutação
                num_perm = 0
                for i in range(n):
                    for j in range(n):
                        num_perm += W[i,j] * y_perm[i] * y_perm[j]
                
                I_perm = (n / S0) * (num_perm / denominator)
                
                # Verificar se o resultado é válido
                if np.isfinite(I_perm):
                    I_permuted.append(I_perm)
                    valid_permutations += 1
                    
            except Exception:
                continue
        
        if valid_permutations < permutations * 0.5:
            raise Exception(f"Muitas permutações falharam ({permutations - valid_permutations} de {permutations}). "
                          "Isso pode indicar problemas com os dados.")
        
        I_permuted = np.array(I_permuted)
        
        # Calcular p-valor baseado nas permutações válidas
        if I_observed >= E_I:
            p_value = np.sum(I_permuted >= I_observed) / valid_permutations
        else:
            p_value = np.sum(I_permuted <= I_observed) / valid_permutations
        
        # P-valor bilateral
        p_value = min(2 * p_value, 1.0)
        
        # Variância empírica das permutações
        var_I = np.var(I_permuted) if len(I_permuted) > 1 else 0
        z_score = (I_observed - E_I) / np.sqrt(var_I) if var_I > 0 else 0
        
        return {
            'I': I_observed,
            'E_I': E_I,
            'Var_I': var_I,
            'z_score': z_score,
            'p_value': p_value,
            'permutations': valid_permutations,
            'total_attempted': permutations,
            'significance_level': self.params['significance_level']
        }
    
    def calculate_advanced_lisa(self, values, W):
        """Calcula indicadores LISA com classificação de padrões"""
        n = len(values)
        y = values - np.mean(values)
        
        # Calcular estatísticas LISA para cada observação
        lisa_values = []
        z_scores = []
        p_values = []
        spatial_patterns = []
        
        # Usar menos permutações para LISA para melhor performance
        permutations = min(self.params['permutations'] // 2, 99)
        
        for i in range(n):
            # LISA local observado
            lisa_i_obs = y[i] * np.sum(W[i] * y)
            lisa_values.append(lisa_i_obs)
            
            # Teste de permutação local simplificado
            lisa_i_perm = []
            valid_local_perms = 0
            
            for perm_j in range(permutations):
                try:
                    y_perm = np.random.permutation(y)
                    lisa_i = y[i] * np.sum(W[i] * y_perm)
                    
                    if np.isfinite(lisa_i):
                        lisa_i_perm.append(lisa_i)
                        valid_local_perms += 1
                        
                except Exception:
                    continue
            
            if valid_local_perms == 0:
                # Se nenhuma permutação for válida, usar valores padrão
                p_val = 1.0
                z_i = 0.0
            else:
                lisa_i_perm = np.array(lisa_i_perm)
                
                # P-valor baseado em permutações
                if lisa_i_obs >= 0:
                    p_val = np.sum(lisa_i_perm >= lisa_i_obs) / valid_local_perms
                else:
                    p_val = np.sum(lisa_i_perm <= lisa_i_obs) / valid_local_perms
                
                p_val = min(2 * p_val, 1.0)  # P-valor bilateral
                
                # Z-score baseado na distribuição das permutações
                var_perm = np.var(lisa_i_perm) if len(lisa_i_perm) > 1 else 0
                z_i = (lisa_i_obs - np.mean(lisa_i_perm)) / np.sqrt(var_perm) if var_perm > 0 else 0
            
            p_values.append(p_val)
            z_scores.append(z_i)
            
            # Classificar padrão espacial
            original_value = values[i]
            mean_value = np.mean(values)
            neighbors_mean = np.sum(W[i] * values) if np.sum(W[i]) > 0 else mean_value
            
            if p_val <= self.params['significance_level']:
                if original_value > mean_value and neighbors_mean > mean_value:
                    pattern = "High-High"
                elif original_value < mean_value and neighbors_mean < mean_value:
                    pattern = "Low-Low"
                elif original_value > mean_value and neighbors_mean < mean_value:
                    pattern = "High-Low"
                elif original_value < mean_value and neighbors_mean > mean_value:
                    pattern = "Low-High"
                else:
                    pattern = "Não significativo"
            else:
                pattern = "Não significativo"
            
            spatial_patterns.append(pattern)
        
        # Debug: verificar resultados gerados
        safe_log_message(f"LISA calculado para {len(lisa_values)} observações", "Spatial Analysis", "info")
        safe_log_message(f"Padrões encontrados: {set(spatial_patterns)}", "Spatial Analysis", "info")
        
        # Contar padrões significativos
        significant_count = sum(1 for p in p_values if p <= self.params['significance_level'])
        safe_log_message(f"Padrões significativos: {significant_count} de {len(p_values)}", "Spatial Analysis", "info")
        
        return {
            'lisa_values': lisa_values,
            'z_scores': z_scores,
            'p_values': p_values,
            'spatial_patterns': spatial_patterns,
            'significance_level': self.params['significance_level']
        }
    
    def create_lisa_layer(self, features, lisa_results):
        """Cria nova camada com resultados LISA detalhados"""
        original_layer = self.params['layer']
        layer_name = f"{original_layer.name()}_LISA_Analise"
        
        safe_log_message(f"Criando camada LISA com {len(features)} features", "Spatial Analysis", "info")
        
        # Criar nova camada
        geom_type = QgsWkbTypes.displayString(original_layer.wkbType())
        crs_authid = original_layer.crs().authid()
        
        new_layer = QgsVectorLayer(
            f"{geom_type}?crs={crs_authid}", 
            layer_name, 
            "memory"
        )
        
        if not new_layer.isValid():
            raise Exception(f"Não foi possível criar a camada de resultados. Tipo: {geom_type}, CRS: {crs_authid}")
        
        # Iniciar edição
        new_layer.startEditing()
        
        # Copiar apenas campos essenciais da camada original
        original_fields = original_layer.fields()
        essential_fields = []
        
        # Adicionar campo ID e campo analisado
        id_field_added = False
        for field in original_fields:
            if field.name().lower() in ['id', 'fid', 'objectid', self.params['field_name'].lower()]:
                essential_fields.append(field)
                if field.name().lower() in ['id', 'fid', 'objectid']:
                    id_field_added = True
        
        # Se não há campo ID, criar um
        if not id_field_added:
            essential_fields.append(QgsField("ID", QVariant.Int))
        
        new_layer.dataProvider().addAttributes(essential_fields)
        
        # Adicionar campos específicos para resultados LISA
        lisa_fields = [
            QgsField("LISA_I", QVariant.Double, "double", 15, 6),
            QgsField("LISA_Z", QVariant.Double, "double", 15, 6), 
            QgsField("LISA_P", QVariant.Double, "double", 15, 6),
            QgsField("Padrao_Espacial", QVariant.String, "string", 25),
            QgsField("Significativo", QVariant.String, "string", 10),
            QgsField("Categoria_Visual", QVariant.String, "string", 20)
        ]
        
        new_layer.dataProvider().addAttributes(lisa_fields)
        new_layer.updateFields()
        
        safe_log_message(f"Camada criada com {new_layer.fields().count()} campos", "Spatial Analysis", "info")
        
        # Adicionar features com resultados
        new_features = []
        
        for i, feature in enumerate(features):
            if i >= len(lisa_results['lisa_values']):
                safe_log_message(f"Aviso: Feature {i} não tem resultado LISA correspondente", "Spatial Analysis", "warning")
                continue
                
            new_feature = QgsFeature(new_layer.fields())
            
            # Copiar geometria
            geom = feature.geometry()
            if geom and not geom.isEmpty():
                new_feature.setGeometry(geom)
            else:
                safe_log_message(f"Aviso: Feature {i} tem geometria inválida", "Spatial Analysis", "warning")
                continue
            
            # Copiar atributos essenciais
            for field in essential_fields[:-6]:  # Excluir os campos LISA que serão adicionados separadamente
                field_name = field.name()
                if field_name in [f.name() for f in original_fields]:
                    value = feature[field_name]
                    new_feature[field_name] = value
            
            # Adicionar ID se necessário
            if not id_field_added:
                new_feature["ID"] = i + 1
            
            # Adicionar resultados LISA
            try:
                new_feature["LISA_I"] = float(lisa_results['lisa_values'][i])
                new_feature["LISA_Z"] = float(lisa_results['z_scores'][i])
                new_feature["LISA_P"] = float(lisa_results['p_values'][i])
                new_feature["Padrao_Espacial"] = str(lisa_results['spatial_patterns'][i])
                
                # Classificar significância
                p_val = lisa_results['p_values'][i]
                significance_level = lisa_results['significance_level']
                
                if p_val <= significance_level:
                    new_feature["Significativo"] = "Sim"
                    new_feature["Categoria_Visual"] = str(lisa_results['spatial_patterns'][i])
                else:
                    new_feature["Significativo"] = "Não"
                    new_feature["Categoria_Visual"] = "Não significativo"
                    
            except Exception as e:
                safe_log_message(f"Erro ao processar feature {i}: {str(e)}", "Spatial Analysis", "warning")
                continue
            
            new_features.append(new_feature)
        
        # Adicionar todas as features de uma vez
        if new_features:
            success = new_layer.dataProvider().addFeatures(new_features)
            if not success:
                raise Exception("Falha ao adicionar features à camada de resultados")
            
            # Confirmar edições
            commit_success = new_layer.commitChanges()
            if not commit_success:
                safe_log_message("Aviso: Problemas ao confirmar edições da camada", "Spatial Analysis", "warning")
            
            # Verificar se os dados foram realmente adicionados
            feature_count = new_layer.featureCount()
            safe_log_message(f"Verificação: Camada tem {feature_count} features após commit", "Spatial Analysis", "info")
            
            if feature_count == 0:
                safe_log_message("ERRO: Camada criada mas sem features!", "Spatial Analysis", "warning")
                # Tentar adicionar novamente de forma mais simples
                new_layer.startEditing()
                for feature in new_features[:3]:  # Tentar apenas as primeiras 3 como teste
                    new_layer.addFeature(feature)
                new_layer.commitChanges()
                safe_log_message(f"Tentativa de recuperação: {new_layer.featureCount()} features", "Spatial Analysis", "info")
            
            # Adicionar ao projeto
            QgsProject.instance().addMapLayer(new_layer)
            
            # Fazer zoom para a camada
            if hasattr(iface, 'mapCanvas') and new_layer.extent().isFinite():
                iface.mapCanvas().setExtent(new_layer.extent())
                iface.mapCanvas().refresh()
                
            safe_log_message(f"Camada LISA criada com sucesso: {feature_count} features adicionadas", "Spatial Analysis", "info")
            
            return new_layer
        else:
            new_layer.rollBack()
            raise Exception("Nenhuma feature válida foi criada para a camada de resultados")
    
    def create_automatic_visualization(self, layer, lisa_results):
        """Cria simbolização automática baseada nos padrões LISA detectados"""
        
        safe_log_message("Iniciando criação de visualização automática", "Spatial Analysis", "info")
        
        if not layer or not layer.isValid():
            safe_log_message("Camada inválida para visualização", "Spatial Analysis", "warning")
            return
        
        # Verificar se o campo existe
        field_name = "Categoria_Visual"
        field_index = layer.fields().indexOf(field_name)
        
        if field_index == -1:
            safe_log_message(f"Campo {field_name} não encontrado na camada", "Spatial Analysis", "warning")
            return
        
        # Obter valores únicos do campo para verificar
        unique_values = layer.uniqueValues(field_index)
        safe_log_message(f"Valores únicos encontrados: {list(unique_values)}", "Spatial Analysis", "info")
        
        # Definir cores para cada tipo de padrão espacial
        pattern_colors = {
            "High-High": "#FF0000",        # Vermelho - Hotspots
            "Low-Low": "#0000FF",          # Azul - Coldspots  
            "High-Low": "#FFA500",         # Laranja - Outliers positivos
            "Low-High": "#800080",         # Roxo - Outliers negativos
            "Não significativo": "#C8C8C8" # Cinza claro
        }
        
        # Criar categorias para o renderer
        categories = []
        
        for pattern, color_hex in pattern_colors.items():
            if pattern in unique_values:  # Só criar categoria se o padrão existe nos dados
                try:
                    # Criar símbolo baseado no tipo de geometria
                    if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                        symbol = QgsFillSymbol.createSimple({
                            'color': color_hex,
                            'outline_color': 'black',
                            'outline_width': '0.3',
                            'outline_style': 'solid'
                        })
                    elif layer.geometryType() == QgsWkbTypes.PointGeometry:
                        symbol = QgsMarkerSymbol.createSimple({
                            'color': color_hex,
                            'outline_color': 'black',
                            'outline_width': '0.5',
                            'size': '3'
                        })
                    else:  # LineGeometry
                        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                        symbol.setColor(QColor(color_hex))
                    
                    category = QgsRendererCategory(pattern, symbol, pattern)
                    categories.append(category)
                    safe_log_message(f"Categoria criada para: {pattern}", "Spatial Analysis", "info")
                    
                except Exception as e:
                    safe_log_message(f"Erro ao criar símbolo para {pattern}: {str(e)}", "Spatial Analysis", "warning")
                    continue
        
        if not categories:
            safe_log_message("Nenhuma categoria foi criada para visualização", "Spatial Analysis", "warning")
            return
        
        try:
            # Criar renderer categorizado
            renderer = QgsCategorizedSymbolRenderer(field_name, categories)
            
            # Aplicar o renderer à camada
            layer.setRenderer(renderer)
            
            # Forçar atualização da camada
            layer.triggerRepaint()
            
            # Atualizar legenda
            if hasattr(iface, 'layerTreeView'):
                iface.layerTreeView().refreshLayerSymbology(layer.id())
            
            # Atualizar canvas
            if hasattr(iface, 'mapCanvas'):
                iface.mapCanvas().refresh()
            
            safe_log_message(f"Visualização aplicada com sucesso: {len(categories)} categorias", "Spatial Analysis", "info")
            
        except Exception as e:
            safe_log_message(f"Erro ao aplicar visualização: {str(e)}", "Spatial Analysis", "warning")
    
    def save_layer_to_file(self, layer):
        """Salva a camada como arquivo permanente (Shapefile)"""
        try:
            import os
            import tempfile
            
            # Criar nome do arquivo na pasta temporária do usuário
            temp_dir = tempfile.gettempdir()
            original_name = self.params['layer'].name()
            file_name = f"{original_name}_LISA_Analise.shp"
            file_path = os.path.join(temp_dir, file_name)
            
            # Se arquivo já existe, criar nome único
            counter = 1
            while os.path.exists(file_path):
                file_name = f"{original_name}_LISA_Analise_{counter}.shp"
                file_path = os.path.join(temp_dir, file_name)
                counter += 1
            
            # Salvar como Shapefile
            error = QgsVectorFileWriter.writeAsVectorFormat(
                layer,
                file_path,
                "utf-8",
                layer.crs(),
                "ESRI Shapefile"
            )
            
            if error == QgsVectorFileWriter.NoError:
                safe_log_message(f"Arquivo salvo com sucesso: {file_path}", "Spatial Analysis", "info")
                return file_path
            else:
                safe_log_message(f"Erro ao salvar arquivo: {error}", "Spatial Analysis", "warning")
                return None
                
        except Exception as e:
            safe_log_message(f"Erro ao salvar arquivo: {str(e)}", "Spatial Analysis", "warning")
            return None


class AdvancedResultsDialog(QDialog):
    """Dialog avançado para mostrar resultados detalhados da análise"""
    
    def __init__(self, results):
        super().__init__()
        self.results = results
        self.setupUi()
        
    def setupUi(self):
        """Configura interface detalhada de resultados"""
        self.setWindowTitle("Resultados da Análise de Autocorrelação Espacial")
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Criar widget de texto para resultados detalhados
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        # Gerar texto detalhado dos resultados
        results_html = self.generate_detailed_results()
        self.results_text.setHtml(results_html)
        
        layout.addWidget(self.results_text)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def generate_detailed_results(self):
        """Gera relatório HTML detalhado dos resultados"""
        html = "<html><body style='font-family: Arial, sans-serif;'>"
        html += "<h2 style='color: #2E5984;'>Relatório de Análise de Autocorrelação Espacial</h2>"
        
        if 'moran' in self.results:
            moran = self.results['moran']
            html += "<h3 style='color: #4A90A4;'>I de Moran Global</h3>"
            html += f"<p><strong>Estatística I de Moran:</strong> {moran['I']:.6f}</p>"
            html += f"<p><strong>Valor Esperado (H₀):</strong> {moran['E_I']:.6f}</p>"
            html += f"<p><strong>Z-score:</strong> {moran['z_score']:.4f}</p>"
            html += f"<p><strong>P-valor:</strong> {moran['p_value']:.6f}</p>"
            html += f"<p><strong>Teste baseado em:</strong> {moran['permutations']} permutações válidas</p>"
            
            # Interpretação estatística
            html += "<h4>Interpretação:</h4>"
            significance_level = moran['significance_level']
            
            if moran['p_value'] < significance_level:
                if moran['I'] > moran['E_I']:
                    interpretation = f"<span style='color: red;'><strong>Autocorrelação espacial POSITIVA significativa</strong></span> (α = {significance_level})"
                    explanation = "Valores similares tendem a estar agrupados espacialmente."
                else:
                    interpretation = f"<span style='color: blue;'><strong>Autocorrelação espacial NEGATIVA significativa</strong></span> (α = {significance_level})"
                    explanation = "Valores diferentes tendem a estar próximos espacialmente."
            else:
                interpretation = f"<span style='color: gray;'><strong>Distribuição espacial aleatória</strong></span> (α = {significance_level})"
                explanation = "Não há evidência de padrão espacial significativo nos dados."
            
            html += f"<p>{interpretation}</p>"
            html += f"<p><em>{explanation}</em></p>"
        
        if 'lisa' in self.results:
            lisa = self.results['lisa']
            html += "<h3 style='color: #4A90A4;'>Análise LISA (Indicadores Locais)</h3>"
            
            # Resumo dos padrões encontrados
            patterns = lisa['spatial_patterns']
            pattern_counts = {}
            for pattern in patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            html += "<h4>Resumo dos Padrões Espaciais Locais:</h4>"
            html += "<ul>"
            
            total_obs = len(patterns)
            for pattern, count in pattern_counts.items():
                percentage = (count / total_obs) * 100
                if pattern == "High-High":
                    description = "Hotspots (valores altos cercados por valores altos)"
                elif pattern == "Low-Low":
                    description = "Coldspots (valores baixos cercados por valores baixos)"
                elif pattern == "High-Low":
                    description = "Outliers positivos (valores altos em áreas de valores baixos)"
                elif pattern == "Low-High":
                    description = "Outliers negativos (valores baixos em áreas de valores altos)"
                else:
                    description = "Sem padrão espacial significativo"
                
                html += f"<li><strong>{pattern}:</strong> {count} observações ({percentage:.1f}%) - {description}</li>"
            
            html += "</ul>"
            
            # Informações sobre significância
            significant_count = sum(1 for p in lisa['p_values'] if p <= lisa['significance_level'])
            significance_percentage = (significant_count / total_obs) * 100
            
            html += f"<p><strong>Observações com padrão espacial significativo:</strong> {significant_count} de {total_obs} ({significance_percentage:.1f}%)</p>"
            html += f"<p><strong>Nível de significância utilizado:</strong> α = {lisa['significance_level']}</p>"
            
            if 'lisa_layer' in self.results:
                layer_name = self.results['lisa_layer'].name()
                html += f"<p><strong>Camada criada:</strong> {layer_name}</p>"
                
                if 'saved_file' in self.results:
                    html += f"<p><strong>Arquivo salvo em:</strong> <code>{self.results['saved_file']}</code></p>"
                    html += "<p><em>O arquivo foi salvo permanentemente e pode ser usado em outros projetos.</em></p>"
                else:
                    html += "<p><em>Os resultados foram adicionados como uma camada temporária no projeto atual.</em></p>"
                    
                html += "<p><em>A camada possui simbolização automática baseada nos padrões detectados.</em></p>"
        
        # Informações metodológicas
        html += "<hr>"
        html += "<h3 style='color: #4A90A4;'>Informações Metodológicas</h3>"
        html += "<p><strong>Método de análise:</strong> Autocorrelação espacial com testes de permutação</p>"
        html += "<p><strong>Vantagens do método:</strong></p>"
        html += "<ul>"
        html += "<li>Testes de significância robustos sem assumir normalidade</li>"
        html += "<li>Adequado para dados de contagem e distribuições não-normais</li>"
        html += "<li>Identificação de padrões locais e globais</li>"
        html += "<li>Visualização automática dos resultados</li>"
        html += "</ul>"
        
        html += "</body></html>"
        return html


# Função para inicializar o plugin
def classFactory(iface):
    """Função obrigatória para carregar o plugin no QGIS"""
    return SpatialAnalysisPlugin(iface)