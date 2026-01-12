from nicegui import ui

def show_help():
    with ui.dialog() as dialog, ui.card().classes('bg-slate-900 text-slate-200 border-2 border-blue-900 w-[600px]'):
        with ui.column().classes('w-full p-6'):
            # Title & Brand
            ui.label("A2UI-Borg Master Hub").classes('text-2xl font-black text-blue-500 uppercase tracking-tighter')
            ui.label("System Directive & Documentation").classes('text-[10px] text-slate-500 font-bold mb-4 tracking-widest')
            
            ui.separator().classes('bg-blue-900 mb-4')
            
            # Mission Statement
            with ui.column().classes('gap-1 mb-4'):
                ui.label("WHAT IS A2UI-BORG?").classes('text-[10px] text-blue-400 font-bold')
                ui.label(
                    "A2UI-Borg is an autonomous neural interface system designed for instant "
                    "assimilation of user requirements into functional UI components. "
                    "It serves as the technological 'favorite pet' of the Borg Queen – "
                    "highly customizable, efficient, and aesthetically perfected."
                ).classes('text-sm text-slate-300 leading-relaxed')

            # Features
            with ui.column().classes('gap-1 mb-4'):
                ui.label("CORE FEATURES:").classes('text-[10px] text-blue-400 font-bold')
                with ui.column().classes('pl-2 gap-0'):
                    ui.label("• Neural Assimilation: Converts natural language into JSON-DNA.").classes('text-xs')
                    ui.label("• Evolution Snapshots: Locally archives every UI mutation.").classes('text-xs')
                    ui.label("• Collective Knowledge: Dynamic control via help.json.").classes('text-xs')
                    ui.label("• DNA Export: Direct access to generated code for copy-paste.").classes('text-xs')

            ui.separator().classes('bg-blue-900/50 my-2')

            # Architect Info
            with ui.row().classes('w-full justify-between items-end mt-2'):
                with ui.column():
                    ui.label("ARCHITECT:").classes('text-[10px] text-slate-400 font-bold')
                    ui.label("Michael Barlozewski").classes('text-lg font-bold text-white tracking-tight')
                    ui.link("g.dev/avx", "https://g.dev/avx").classes('text-blue-500 text-xs font-mono')
                
                with ui.column().classes('items-end'):
                    ui.label("VERSION:").classes('text-[10px] text-slate-400 font-bold')
                    ui.label("1.9.3 Global").classes('text-xs italic text-slate-500')

            ui.button('DEACTIVATE DIALOG', on_click=dialog.close).classes('w-full mt-6 bg-blue-800 font-bold hover:bg-blue-600 transition-all')
            
    dialog.open()
