# WinRAM 🚀

O **WinRAM** é um otimizador de sistema leve e potente para Windows, escrito em Python. Ele foca em liberar memória RAM e limpar arquivos temporários que acumulam e tornam o sistema lento.

## ✨ Funcionalidades
- **Otimização de RAM:** Utiliza chamadas nativas à API do Windows (`EmptyWorkingSet`) para forçar processos a liberar memória não utilizada de volta ao sistema.
- **Limpeza de Arquivos Temporários:** Remove resíduos do sistema em `%TEMP%`, `C:\Windows\Temp` e `C:\Windows\Prefetch`.
- **Dashboard em Tempo Real:** Acompanhe o uso de memória RAM com uma interface moderna e intuitiva.
- **Segurança:** Trata arquivos em uso e falhas de permissão graciosamente.

## 🚀 Como usar
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o programa como **Administrador** para melhores resultados:
   ```bash
   python main.py
   ```

## 🎨 Interface Premium
Construído com `CustomTkinter` para uma experiência visual de alto nível no Windows 10 e 11.

---
*Desenvolvido com o auxílio do AG Toolkit.*
