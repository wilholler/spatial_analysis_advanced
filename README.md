# 🗺️ Plugin QGIS - Análise de Autocorrelação Espacial

[![QGIS Version](https://img.shields.io/badge/QGIS-3.0%2B-green.svg)](https://qgis.org/)
[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://python.org/)
[![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)]()
[![IBGE Data](https://img.shields.io/badge/IBGE-Compatible-orange.svg)]()

Plugin do QGIS, em português, para análise de **I de Moran** e **LISA (Local Indicators of Spatial Association)**, para polígonos, com visualização automática e tratamento especial para dados numéricos. Desenvolvido inicialmente para análise de dados do IBGE sobre silvicultura, mas com ampla aplicabilidade em diversas áreas.

---

## 🌲 Aplicação Específica: Dados IBGE de Silvicultura

### 📊 **Dados Suportados do IBGE**

#### **PEVS - Produção da Extração Vegetal e da Silvicultura**
- ✅ **Produção de madeira** por espécie e município
- ✅ **Área plantada** com florestas cultivadas
- ✅ **Valor da produção** silvicultural
- ✅ **Séries históricas** para análise temporal

#### **Censo Agropecuário**
- ✅ **Estabelecimentos** com silvicultura
- ✅ **Área destinada** a florestas plantadas
- ✅ **Tipos de essências** florestais
- ✅ **Finalidade da produção** (papel, energia, etc.)

#### **Malhas Territoriais**
- ✅ **Municípios** brasileiros
- ✅ **Microrregiões** e mesorregiões
- ✅ **Estados** e regiões
- ✅ **Compatibilidade** com limites administrativos IBGE

### 🔬 **Análises Típicas em Silvicultura**

#### **Clusters de Produção**
```python
# Exemplo: Produção de eucalipto (m³) por município
Padrões esperados:
├── Hotspots: Sul/Sudeste (tradição silvicultural)
├── Coldspots: Norte/Nordeste (menor aptidão)
├── Outliers: Municípios isolados com grandes projetos
└── Tendência: Expansão para Centro-Oeste
```

#### **Análise de Produtividade**
```python
# Exemplo: Produtividade (m³/ha) por região
Fatores espaciais:
├── Clima e solo (autocorrelação natural)
├── Tecnologia (difusão espacial)
├── Logística (proximidade de indústrias)
└── Políticas (incentivos regionais)
```

### 🌍 **Importância para Pesquisa Brasileira**
- **Zoneamento** de aptidão silvicultural
- **Melhoramento genético** com base territorial
- **Sustentabilidade** de sistemas florestais
- **Políticas públicas** baseadas em evidências

#### **Setor Florestal Brasileiro**
- **Planejamento estratégico** de plantios
- **Identificação de oportunidades** regionais
- **Monitoramento** de performance setorial
- **Análise de competitividade** territorial

---

## 📋 Índice

- [✨ Funcionalidades](#-funcionalidades)
- [🚀 Instalação Rápida](#-instalação-rápida)
- [📊 Como Usar](#-como-usar)
- [🎯 Casos de Uso](#-casos-de-uso)
- [📈 Exemplos Práticos](#-exemplos-práticos)
- [🔧 Requisitos](#-requisitos)
- [📖 Documentação Técnica](#-documentação-técnica)
- [🤝 Contribuição](#-contribuição)
- [📜 Licença](#-licença)
- [📚 Citação Acadêmica](#-citação-acadêmica)

---

## ✨ Funcionalidades

### 🌍 **Análise Global de Moran**
- **Testes de permutação robustos** (distribuição-livre)
- **Múltiplas configurações** de vizinhança espacial
- **Interpretação automática** dos resultados
- **Relatórios detalhados** com significância estatística

### 📍 **Análise LISA Local**
- **Identificação automática** de hotspots e coldspots
- **Classificação em 4 padrões**: High-High, Low-Low, High-Low, Low-High
- **Mapas temáticos** com cores intuitivas
- **Testes de significância** locais

### 🎨 **Visualização**
- **Simbolização automática** baseada em padrões detectados
- **Cores científicas**: 🔴 Hotspots, 🔵 Coldspots, 🟠 Outliers
- **Legendas explicativas** com interpretação

### 📊 **Tratamento Especializado de Dados**
- **Dados de contagem** (distribuição de Poisson) com transformação Freeman-Tukey
- **Dados contínuos** (distribuição Gaussiana)
- **Taxas e proporções** com transformações apropriadas
- **Validação automática** e limpeza de dados

### 🔧 **Interface Intuitiva**
- **Design educativo**
- **Validações** dos parâmetros
- **Progresso** durante execução
- **Relatório** dos resultados

---

## 🚀 Instalação Rápida

### 📥 **Método 1: Download Direto**

1. **Baixe** a versão mais recente:
   ```bash
   git clone https://github.com/wilholler/spatial_analysis_advanced.git
   cd spatial_analysis_advanced
   ```

2. **Localize** o diretório de plugins do QGIS:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`

3. **Copie** a pasta para o diretório de plugins
4. **Reinicie** o QGIS
5. **Ative** o plugin em: `Complementos > Gerenciar e Instalar Complementos`

### 📦 **Método 2: Instalação de Dependências**

```bash
# Para Windows (OSGeo4W Shell como administrador)
python -m pip install scipy numpy

# Para Linux/macOS
pip3 install scipy numpy

# Verificar instalação
python -c "import scipy; print('✓ SciPy instalado com sucesso')"
```
 Instalação direta: baixe o ZIP e carregue em complementos do QGis
---

## 📊 Como Usar

### 🎯 **Fluxo Básico**

1. **Carregue** sua camada vetorial (polígono) no QGIS
2. **Acesse** o plugin: `Vetor > Análise Espacial > Análise Espacial Avançada`
3. **Configure** os parâmetros:

#### **1️⃣ Configuração dos Dados**
```
Camada vetorial (Polígono): [Sua camada]
Campo para análise: [Campo numérico]
Tipo de dados: [Contagem/Contínuo/Taxa]
```

#### **2️⃣ Vizinhança Espacial**
```
Queen Adjacency     → Regiões contíguas (polígonos)
K-vizinhos         → Pontos dispersos (K=3 ou maior)
Distância fixa     → Influência por proximidade
```

#### **3️⃣ Análises**
```
☑ I de Moran Global     → Padrão geral
☑ LISA Local           → Hotspots/Coldspots
☑ Mapas temáticos      → Visualização automática
☑ Arquivo permanente   → Salvar resultados
```

4. **Execute** e examine os resultados!

### 🎨 **Interpretando os Resultados**

#### **I de Moran Global**
| Valor | Interpretação |
|-------|---------------|
| **I > E[I], p < 0.05** | 🔴 **Autocorrelação POSITIVA** - Valores similares agrupados |
| **I < E[I], p < 0.05** | 🔵 **Autocorrelação NEGATIVA** - Valores diferentes próximos |
| **p ≥ 0.05** | ⚪ **Distribuição ALEATÓRIA** - Sem padrão espacial |

#### **Padrões LISA Locais**
| Padrão | Cor | Significado |
|--------|-----|-------------|
| **High-High** | 🔴 Vermelho | **Hotspots** - Valores altos cercados por valores altos |
| **Low-Low** | 🔵 Azul | **Coldspots** - Valores baixos cercados por valores baixos |
| **High-Low** | 🟠 Laranja | **Outliers positivos** - Valor alto isolado |
| **Low-High** | 🟣 Roxo | **Outliers negativos** - Valor baixo isolado |

---

## 🎯 Casos de Uso

### 🌲 **Silvicultura e Recursos Florestais (Foco Principal)**
- **Análise de dados do IBGE** sobre produção florestal
- **Distribuição espacial** de plantios florestais
- **Clusters de produtividade** silvicultural
- **Padrões regionais** de manejo florestal
- **Exemplo**: *Produção de eucalipto por município (IBGE/PEVS)*

### 🌾 **Agropecuária e Agricultura**
- **Análise de censos agropecuários** (IBGE/Censo Agro)
- **Produtividade agrícola** por região
- **Distribuição de culturas** e rebanhos
- **Impactos de políticas** agrárias
- **Exemplo**: *Área plantada de soja por microrregião*

### 📊 **Análise Socioeconômica com Dados IBGE**
- **Censo Demográfico** - padrões populacionais
- **PNAD/PNADC** - mercado de trabalho regional
- **PIB Municipal** - desenvolvimento econômico
- **Índices sociais** por território
- **Exemplo**: *Renda per capita por setor censitário*

### 🏥 **Epidemiologia e Saúde Pública**
- **Análise de clusters** de doenças por região
- **Identificação de hotspots** de incidência
- **Monitoramento de surtos** em tempo real
- **Correlação com fatores** ambientais
- **Exemplo**: *Casos de dengue por município*

### 🚔 **Segurança Pública**
- **Mapeamento de criminalidade** urbana
- **Identificação de áreas** críticas
- **Planejamento de policiamento** preventivo
- **Análise temporal-espacial**
- **Exemplo**: *Ocorrências policiais por distrito*

### 🌱 **Estudos Ambientais**
- **Qualidade do ar/água** por estação de monitoramento
- **Distribuição de espécies** (biodiversidade)
- **Impactos de mudanças climáticas**
- **Cobertura vegetal** e desmatamento
- **Exemplo**: *Índices de desmatamento por região*

---

## 📈 Exemplos Práticos

### 🌲 **Exemplo 1: Análise de Silvicultura (IBGE/PEVS)**

```python
# Dados: Produção de eucalipto em metros cúbicos por município
# Fonte: IBGE - Produção da Extração Vegetal e da Silvicultura (PEVS)
Configuração:
├── Tipo de dados: "Contagem (Poisson)"
├── Vizinhança: "Queen Adjacency" 
├── Significância: 0.05
└── Permutações: 999

Resultados esperados:
├── I de Moran: 0.52 (p < 0.001) → Forte autocorrelação positiva
├── Hotspots: Regiões Sul e Sudeste (tradição silvicultural)
├── Coldspots: Norte e Nordeste (menor produção)
└── Interpretação: Produção concentrada em polos silviculturais
```

### 🌾 **Exemplo 2: Censo Agropecuário IBGE**

```python
# Dados: Área plantada de soja (hectares) por município
# Fonte: IBGE - Censo Agropecuário
Configuração:
├── Tipo de dados: "Contínuo (Gaussiano)"
├── Vizinhança: "K-vizinhos (K=8)"
├── Significância: 0.01
└── Permutações: 999

Resultados esperados:
├── I de Moran: 0.67 (p < 0.001) → Padrão espacial muito forte
├── Hotspots: Centro-Oeste (Cerrado), Sul (tradição agrícola)
├── Coldspots: Norte (Amazônia), Nordeste (semiárido)
└── Interpretação: Concentração na fronteira agrícola
```

### 🏘️ **Exemplo 3: Demografia IBGE (Censo)**

```python
# Dados: Densidade populacional por setor censitário
# Fonte: IBGE - Censo Demográfico
Configuração:
├── Tipo de dados: "Contínuo (Gaussiano)"
├── Vizinhança: "Distância fixa (5km)"
├── Significância: 0.05
└── Permutações: 599

Resultados esperados:
├── I de Moran: 0.43 (p < 0.001) → Padrão de concentração urbana
├── Hotspots: Centros urbanos, regiões metropolitanas
├── Coldspots: Áreas rurais, regiões remotas
└── Interpretação: Concentração populacional em núcleos urbanos
```

---

## 🔧 Requisitos

### 🖥️ **Sistema**
- **QGIS**: 3.0 ou superior (testado até 3.40+)
- **Python**: 3.6+ (incluído no QGIS)
- **Sistema Operacional**: Windows, macOS, Linux

### 📚 **Dependências Python**
```python
numpy>=1.19.0          # Operações numéricas
scipy>=1.6.0           # Estatística avançada e triangulação
```

### 📊 **Dados de Entrada**
- **Formato**: Shapefile, GeoPackage, PostGIS, etc.
- **Geometria**: Polígonos
- **Campos**: Pelo menos um campo numérico para análise
- **Mínimo**: 3 feições (recomendado: 20+ para resultados robustos)

### 💾 **Recursos Computacionais**
- **RAM**: 4GB+ (datasets grandes do IBGE: 8GB+)
- **Processamento**: Depende do número de permutações
  - 999 permutações: ~10-30 segundos
  - 9999 permutações: ~2-5 minutos
- **Armazenamento**: Dados IBGE podem ser volumosos (GBs)

---

## 📖 Documentação Técnica

### 🧮 **Métodos Implementados**

#### **I de Moran Global**
```
I = (n/S₀) × [Σᵢ Σⱼ wᵢⱼ(xᵢ - x̄)(xⱼ - x̄)] / [Σᵢ(xᵢ - x̄)²]

Onde:
├── n = número de observações
├── S₀ = soma dos pesos espaciais
├── wᵢⱼ = peso espacial entre regiões i e j
├── xᵢ = valor na região i
└── x̄ = média dos valores
```

#### **LISA Local**
```
Iᵢ = (xᵢ - x̄) × Σⱼ wᵢⱼ(xⱼ - x̄)

Para cada observação i:
├── Calcula influência dos vizinhos
├── Testa significância por permutação
├── Classifica padrão espacial
└── Atribui categoria visual
```

### 🔄 **Transformações de Dados**

#### **Dados de Contagem (Poisson)**
```python
# Transformação Freeman-Tukey
transformed = √x + √(x + 1)
```

#### **Taxas/Proporções**
```python
# Transformação arcsin
transformed = arcsin(√x)
```

### 🎲 **Testes de Permutação**

1. **Embaralhar** valores aleatoriamente preservando localização
2. **Recalcular** estatística para cada permutação
3. **Comparar** valor observado com distribuição empírica
4. **Calcular** p-valor baseado em posição relativa

---

## 🤝 Contribuição

Contribuições são bem-vindas! Este é um projeto acadêmico/científico que beneficia a comunidade de análise espacial.

### 🛠️ **Como Contribuir**

1. **Fork** o repositório
2. **Crie** uma branch para sua funcionalidade:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```
3. **Commit** suas mudanças:
   ```bash
   git commit -m "Adiciona nova funcionalidade X"
   ```
4. **Push** para a branch:
   ```bash
   git push origin feature/nova-funcionalidade
   ```
5. **Abra** um Pull Request

### 🎯 **Áreas para Contribuição**

- 🧮 **Novos métodos estatísticos** (Getis-Ord G*, Join Count, etc.)
- 🌲 **Adaptações para silvicultura** (índices específicos, modelos florestais)
- 📊 **Integração com dados IBGE** (APIs, formatos específicos)
- 🎨 **Melhorias na visualização** (mapas temáticos brasileiros)
- 🌍 **Documentação em português** (tutoriais, exemplos nacionais)
- 🐛 **Correção de bugs** e otimizações
- 🧪 **Testes com dados reais** do IBGE

### 📝 **Diretrizes para Contribuição**

- Mantenha **compatibilidade** com QGIS 3.0+
- Siga **PEP 8** para código Python
- **Interface em português** brasileiro
- Inclua **testes** com dados brasileiros quando possível
- **Documente** métodos em português
- Use **dados IBGE** como exemplos sempre que possível

---

## 🐛 Resolução de Problemas

### ❓ **Problemas Comuns**

#### **"ModuleNotFoundError: No module named 'scipy'"**
```bash
# Solução (Windows OSGeo4W):
1. Abra OSGeo4W Shell como administrador
2. Execute: python -m pip install scipy
3. Reinicie o QGIS
```

#### **"Camada criada mas sem dados"**
```bash
# Verificação:
1. Abra "Ver > Painéis > Log Messages"
2. Procure categoria "Spatial Analysis"
3. Verifique se há erros reportados
4. Teste com dataset menor (10-20 features)
```

#### **"Mapas temáticos não aparecem"**
```bash
# Solução manual:
1. Clique direito na camada LISA
2. Propriedades > Simbologia
3. Mude para "Categorizado"
4. Campo: "Categoria_Visual"
5. Clique "Classificar"
```

### 📞 **Suporte**

- 🐛 **Bugs**: [Abra uma issue](https://github.com/wilholler/spatial_analysis_advanced/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/wilholler/spatial_analysis_advanced/discussions)
- 📧 **Contato**: wilson.holler@embrapa.br

---

## 📜 Licença

Este projeto está licenciado sob **GPL v3** - veja o arquivo [LICENSE](LICENSE) para detalhes.

### 🆓 **Uso Livre**
- ✅ **Uso pessoal** e comercial
- ✅ **Modificação** e redistribuição  
- ✅ **Uso acadêmico** e científico
- ⚠️ **Deve manter** mesma licença
- ⚠️ **Deve creditar** autores originais

---

## 📚 Citação Acadêmica

Se você usar este plugin em pesquisa acadêmica, por favor cite:

### 📝 **Formato APA**
```
Holler, W. (2025). Plugin QGIS - Análise de Autocorrelação Espacial: Ferramentas 
avançadas para análise de I de Moran e LISA (Versão 1.0.0) [Software]. 
Embrapa. https://github.com/wilholler/spatial_analysis_advanced
```

### 📖 **Formato BibTeX**
```bibtex
@software{spatial_analysis_plugin2025,
  author = {Holler, Wilson},
  title = {Plugin QGIS - Análise de Autocorrelação Espacial},
  version = {1.0.0},
  year = {2025},
  institution = {Embrapa},
  url = {https://github.com/wilholler/spatial_analysis_advanced},
  note = {Ferramentas avançadas para análise de I de Moran e LISA}
}
```

### 📊 **Métodos Estatísticos**
Para os métodos implementados, cite também:

- **Moran's I**: Moran, P.A.P. (1950). Notes on continuous stochastic phenomena. *Biometrika*, 37(1/2), 17-23.
- **LISA**: Anselin, L. (1995). Local indicators of spatial association—LISA. *Geographical Analysis*, 27(2), 93-115.
- **Permutation Tests**: Hope, A.C.A. (1968). A simplified Monte Carlo significance test procedure. *Journal of the Royal Statistical Society*, 30(3), 582-598.

---

### 📚 **Inspirações Científicas**
- **GeoDa** - Referência em análise espacial
- **PySAL** - Biblioteca Python para análise espacial
- **spdep (R)** - Métodos de dependência espacial
- **QGIS Community** - Padrões de desenvolvimento

### 🛠️ **Tecnologias Utilizadas**
- **QGIS** - Plataforma SIG
- **Python** - Linguagem de programação
- **NumPy/SciPy** - Computação científica
- **PyQt** - Interface gráfica

---

## 📊 Estatísticas do Projeto

![GitHub Stars](https://img.shields.io/github/stars/wilholler/spatial_analysis_advanced?style=social)
![GitHub Forks](https://img.shields.io/github/forks/wilholler/spatial_analysis_advanced?style=social)
![GitHub Issues](https://img.shields.io/github/issues/wilholler/spatial_analysis_advanced)
![GitHub Contributors](https://img.shields.io/github/contributors/wilholler/spatial_analysis_advanced)
