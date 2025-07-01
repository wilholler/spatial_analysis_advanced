#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar dependências do Plugin de Análise Espacial
Execute este script para instalar automaticamente as bibliotecas necessárias
"""

import sys
import subprocess
import os
import platform

def check_admin():
    """Verifica se o script está sendo executado como administrador"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def install_package(package_name):
    """Instala um pacote Python usando pip"""
    try:
        print(f"Instalando {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✓ {package_name} instalado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Erro ao instalar {package_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro inesperado ao instalar {package_name}: {e}")
        return False

def check_package(package_name):
    """Verifica se um pacote está instalado"""
    try:
        __import__(package_name)
        print(f"✓ {package_name} já está instalado")
        return True
    except ImportError:
        print(f"✗ {package_name} não encontrado")
        return False

def detect_qgis_python():
    """Tenta detectar o interpretador Python do QGIS"""
    system = platform.system()
    
    possible_paths = []
    
    if system == "Windows":
        # Caminhos comuns para instalações do QGIS no Windows
        qgis_versions = ["3.34", "3.32", "3.30", "3.28"]
        for version in qgis_versions:
            possible_paths.extend([
                f"C:\\Program Files\\QGIS {version}\\apps\\Python39\\python.exe",
                f"C:\\Program Files\\QGIS {version}\\apps\\Python38\\python.exe",
                f"C:\\OSGeo4W64\\apps\\Python39\\python.exe",
                f"C:\\OSGeo4W\\apps\\Python39\\python.exe",
            ])
    
    elif system == "Darwin":  # macOS
        possible_paths.extend([
            "/Applications/QGIS.app/Contents/MacOS/bin/python3",
            "/usr/local/bin/python3",
        ])
    
    else:  # Linux
        possible_paths.extend([
            "/usr/bin/python3",
            "/usr/local/bin/python3",
        ])
    
    # Verificar qual caminho existe
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Python do QGIS encontrado em: {path}")
            return path
    
    print("Python do QGIS não encontrado automaticamente.")
    print("Usando o interpretador Python atual:", sys.executable)
    return sys.executable

def main():
    """Função principal do instalador"""
    print("=" * 60)
    print("INSTALADOR DE DEPENDÊNCIAS")
    print("Plugin de Análise de Autocorrelação Espacial para QGIS")
    print("=" * 60)
    
    # Verificar sistema operacional
    system = platform.system()
    print(f"Sistema operacional detectado: {system}")
    print(f"Interpretador Python atual: {sys.executable}")
    
    # Verificar permissões de administrador no Windows
    if system == "Windows" and not check_admin():
        print("\n⚠️  AVISO: Para melhor compatibilidade, execute este script como Administrador")
        print("   Clique com botão direito no arquivo e selecione 'Executar como administrador'")
        input("\nPressione Enter para continuar mesmo assim...")
    
    # Detectar Python do QGIS
    qgis_python = detect_qgis_python()
    
    print("\n" + "-" * 40)
    print("VERIFICANDO DEPENDÊNCIAS EXISTENTES")
    print("-" * 40)
    
    # Lista de dependências necessárias
    required_packages = ["numpy", "scipy"]
    
    # Verificar quais pacotes já estão instalados
    installed = []
    missing = []
    
    for package in required_packages:
        if check_package(package):
            installed.append(package)
        else:
            missing.append(package)
    
    if not missing:
        print("\n🎉 Todas as dependências já estão instaladas!")
        print("\nVocê pode ativar o plugin no QGIS agora.")
        input("\nPressione Enter para sair...")
        return
    
    print("\n" + "-" * 40)
    print("INSTALANDO DEPENDÊNCIAS AUSENTES")
    print("-" * 40)
    
    success_count = 0
    
    for package in missing:
        if install_package(package):
            success_count += 1
        print()  # Linha em branco para separar
    
    print("\n" + "=" * 60)
    print("RESUMO DA INSTALAÇÃO")
    print("=" * 60)
    
    if success_count == len(missing):
        print("🎉 Todas as dependências foram instaladas com sucesso!")
        print("\nPróximos passos:")
        print("1. Reinicie o QGIS")
        print("2. Vá para 'Complementos > Gerenciar e Instalar Complementos'")
        print("3. Na aba 'Instalados', encontre e ative o plugin")
        print("4. O plugin aparecerá no menu 'Vetor > Análise Espacial'")
    else:
        print(f"⚠️  Apenas {success_count} de {len(missing)} dependências foram instaladas.")
        print("\nSe houver problemas, tente:")
        print("1. Execute este script como Administrador (Windows)")
        print("2. Instale manualmente usando:")
        for package in missing:
            print(f"   pip install {package}")
        print("3. Consulte o README.md para instruções detalhadas")
    
    print("\n" + "=" * 60)
    input("Pressione Enter para sair...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstalação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n\nErro inesperado: {e}")
        input("Pressione Enter para sair...")