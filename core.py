import os, json, asyncio, time, re, requests, aiofiles
from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from nicegui import ui, app
from watchfiles import awatch
from loguru import logger
from help import show_help 

# --- 1. CONFIG & BORG-DNA ---
load_dotenv()
NV_KEY = os.getenv("NV_KEY") 
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "mistralai/mistral-large-3-675b-instruct-2512"

class UIElement(BaseModel):
    type: str = Field(..., pattern="^(input|slider|button|switch|label)$")
    label: str
    value: Optional[Union[str, int, float]] = None
    min: Optional[int] = 0
    max: Optional[int] = 100

class UIBitmap(BaseModel):
    title: str
    description: str
    elements: List[UIElement]

class A2UISpecialAgent:
    def __init__(self):
        self.snapshot_dir = "evolution_snapshots"
        self.help_file = "help.json"
        os.makedirs(self.snapshot_dir, exist_ok=True)
        self.knowledge = self.load_knowledge()

    def load_knowledge(self):
        if os.path.exists(self.help_file):
            try:
                with open(self.help_file, 'r', encoding='utf-8') as f: return json.load(f)
            except Exception: return {}
        return {}

    async def sentinel(self):
        async for _ in awatch(self.help_file):
            self.knowledge = self.load_knowledge()
            ui.notify("Collective knowledge synchronized.", color='green')

    async def assimilate(self, user_input: str):
        directives = self.knowledge.get("system_directives", {})
        context = directives.get("admin_expert") if "admin" in user_input.lower() else directives.get("general")
        
        system_msg = f"""You are the A2UI-Borg Agent. CONTEXT: {context}. 
        MANDATORY: Return ONLY a valid JSON object. 
        REQUIRED KEYS: "title", "description", "elements".
        SCHEMA: {{"title": "string", "description": "string", "elements": [{{"type": "input|slider|button|switch|label", "label": "string"}}]}}"""
        
        headers = {"Authorization": f"Bearer {NV_KEY}", "Accept": "application/json"}
        payload = {
            "model": MODEL,
            "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": user_input}],
            "max_tokens": 2048, "temperature": 0.1, "top_p": 1.0
        }

        try:
            response = await asyncio.to_thread(requests.post, INVOKE_URL, headers=headers, json=payload)
            if response.status_code != 200: raise ValueError(f"API Error: {response.status_code}")
            
            res_raw = response.json()['choices'][0]['message']['content']
            json_match = re.search(r'\{.*\}', res_raw, re.DOTALL)
            if not json_match: raise ValueError("No JSON DNA found.")
            
            raw_dict = json.loads(json_match.group(0))

            # BORG-REPAIR LOGIC
            for alt_key in ["ui_elements", "components", "items", "ui"]:
                if alt_key in raw_dict and "elements" not in raw_dict:
                    raw_dict["elements"] = raw_dict.pop(alt_key)
            
            if "title" not in raw_dict: raw_dict["title"] = "Assimilated UI"
            if "description" not in raw_dict: raw_dict["description"] = "Neural Interface"

            blueprint = UIBitmap.model_validate(raw_dict)
            
            fname = f"{self.snapshot_dir}/evo_{int(time.time())}.json"
            async with aiofiles.open(fname, 'w', encoding='utf-8') as f: 
                await f.write(blueprint.model_dump_json(indent=2))
            
            return blueprint, json.dumps(raw_dict)

        except Exception as e:
            logger.error(f"Neural Link Error: {e}")
            fallback = UIBitmap(
                title="Neural Link Recovery",
                description=f"Error: {str(e)[:50]}",
                elements=[{"type": "label", "label": "Borg logic corrected the fields. Please try again."}]
            )
            return fallback, json.dumps(fallback.model_dump())

# --- 2. INTERFACE (MICHAEL'S MASTER HUB) ---
agent = A2UISpecialAgent()
app.on_startup(agent.sentinel)

@ui.page('/')
async def index():
    ui.query('body').classes('bg-slate-950 text-slate-200 font-mono')
    
    with ui.column().classes('w-full max-w-5xl mx-auto p-6'):
        with ui.row().classes('w-full justify-between items-center border-b border-blue-900 pb-4'):
            with ui.column():
                with ui.row().classes('items-center gap-2'):
                    ui.icon('hub', color='blue-500', size='md')
                    ui.label("A2UI-Borg Master Hub").classes('text-2xl font-black text-blue-500 tracking-tighter')
                ui.label("Michael Barlozewski - g.dev/avx").classes('text-[10px] text-slate-400 font-bold uppercase tracking-widest')
            
            with ui.row().classes('items-center gap-4'):
                ui.button(icon='help', on_click=show_help).props('flat round color=blue-400')
                clock = ui.label("").classes('text-slate-500')
                ui.timer(1.0, lambda: clock.set_text(datetime.now().strftime("%H:%M:%S")))

        with ui.row().classes('w-full gap-6 mt-8'):
            with ui.card().classes('w-1/3 bg-slate-900 border-slate-800 p-4 shadow-xl'):
                ui.label("SYSTEM DIRECTIVE").classes('text-[10px] text-blue-400 font-bold mb-2 uppercase')
                user_cmd = ui.textarea(placeholder="Enter command for assimilation...").classes('w-full bg-slate-800 text-sm')
                
                async def trigger():
                    loading.set_visibility(True)
                    blueprint, raw_json = await agent.assimilate(user_cmd.value)
                    render_area.clear()
                    with render_area:
                        ui.label(blueprint.title).classes('text-xl text-blue-300 font-bold')
                        for el in blueprint.elements:
                            if el.type == "input": ui.input(label=el.label).props('dark outlined').classes('w-full mb-2')
                            elif el.type == "slider": 
                                ui.label(el.label).classes('text-[10px] text-slate-400 mt-2')
                                ui.slider(min=el.min, max=el.max, value=50).props('dark')
                            elif el.type == "button": ui.button(el.label).classes('w-full mt-2 bg-blue-700 font-bold')
                            elif el.type == "switch": ui.switch(el.label).props('dark')
                    
                    with code_export_container:
                        code_export_container.clear()
                        with ui.expansion('RAW DNA (JSON CODE)', icon='code').classes('w-full bg-slate-800 text-blue-400 mt-4 rounded'):
                            ui.code(raw_json).classes('text-[10px] bg-transparent')
                            js_cmd = f"navigator.clipboard.writeText({json.dumps(raw_json)})"
                            ui.button('COPY DNA', on_click=lambda: ui.run_javascript(js_cmd)).classes('w-full mt-2 bg-slate-700 text-[10px]')
                    
                    loading.set_visibility(False)

                ui.button("ASSIMILATE", on_click=trigger).classes('w-full h-14 bg-blue-600 font-black mt-2')
                loading = ui.spinner(size='lg').classes('mt-4 self-center'); loading.set_visibility(False)
                code_export_container = ui.column().classes('w-full')

            with ui.column().classes('flex-grow'):
                ui.label("NEURAL VIEWPORT").classes('text-[10px] text-slate-500 mb-2 tracking-widest')
                render_area = ui.card().classes('w-full min-h-[550px] bg-slate-900 border-blue-900/40 border-2 rounded-xl shadow-2xl')

ui.run(title="A2UI-Borg Hub", dark=True, port=8080, reload=False)
