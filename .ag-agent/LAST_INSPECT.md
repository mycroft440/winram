# INSPECT_FILE

Arquivo: main.py
Tamanho bytes: 18899
Linhas totais: 361
E Binario: False
Risco de Edicao: baixo
Sugestao de Ferramenta: replace-text (rt) ou replace-block

## Ancoras Semanticas Provaveis Encontradas
81: self.label_title.pack(anchor="w")
85: self.label_version.pack(anchor="w")
103: self.admin_badge.pack(anchor="e")
128: font=self.font_label, text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
179: command=lambda: self.start_opt("ram_boost"))
198: ctk.CTkLabel(inner, text=icon, font=ctk.CTkFont(size=28)).pack(anchor="w")
200: text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(6, 2))
202: text_color=Theme.TEXT_SECONDARY, wraplength=180, justify="left").pack(anchor="w")
206: command=lambda: self.start_opt(mode))
256: self.console_text.insert("end", "  > Sistema pronto. Selecione um modo de otimização.\n")
301: def start_opt(self, mode):
306: self.console_text.delete("1.0", "end")
311: self.console_text.insert("end", f"  > Iniciando modo {mode_names.get(mode, mode.upper())}...\n")
312: self.console_text.insert("end", f"  > Aguarde enquanto o sistema é otimizado.\n")
315: threading.Thread(target=self.run_task, args=(mode,), daemon=True).start()
331: self.console_text.delete("1.0", "end")
332: self.console_text.insert("end", "  ╔══════════════════════════════════════════╗\n")
333: self.console_text.insert("end", "  ║   ✨  OTIMIZAÇÃO CONCLUÍDA COM SUCESSO   ║\n")
334: self.console_text.insert("end", "  ╚══════════════════════════════════════════╝\n\n")
336: self.console_text.insert("end", f"  ✓  {line}\n")
338: self.console_text.see("end")
343: self.console_text.delete("1.0", "end")
344: self.console_text.insert("end", f"  ✗  ERRO CRÍTICO: {e}\n")