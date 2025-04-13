import uuid
from fasthtml.common import *
import os, uvicorn, requests, replicate
from PIL import Image

gridlink = Link(
    rel="stylesheet",
    href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css",
    type="text/css",
)
app = FastHTML(hdrs=(picolink, gridlink))

replicate_api_token = os.environ.get("REPLICATE_API_KEY")
client = replicate.Client(api_token=replicate_api_token)

# Store our generations
generations = []
folder = f"gens/"
os.makedirs(folder, exist_ok=True)


def generation_preview(g):
    grid_cls = "box col-xs-12 col-sm-6 col-md-4 col-lg-3"
    image_path = f"{g.folder}/{g.id}.png"
    if os.path.exists(image_path):
        return Div(
            Card(
                Img(src=image_path, alt="Card image", cls="card-img-top"),
                Div(P(B("Prompt: "), g.prompt, cls="card-text"), cls="card-body"),
            ),
            id=f"gen-{g.id}",
            cls=grid_cls,
        )
    return Div(
        f"Generating gen {g.id} with prompt {g.prompt}",
        id=f"gen-{g.id}",
        hx_get=f"/gens/{g.id}",
        hx_trigger="every 2s",
        hx_swap="outerHTML",
        cls=grid_cls,
    )


@app.get("/")
def home(session):
    print(session)
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    inp = Input(id="new-prompt", name="prompt", placeholder="Enter a prompt")
    add = Form(
        Group(inp, Button("Generate")),
        hx_post="/",
        target_id="gen-list",
        hx_swap="afterbegin",
    )
    gen_containers = [
        generation_preview(g) for g in generations[-10:]
    ]  # Start with last 10
    gen_list = Div(
        *gen_containers[::-1], id="gen-list", cls="row"
    )  # flexbox container: class = row
    return Title("Image Generation Demo"), Main(
        H1("Magic Image Generation"), add, gen_list, cls="container"
    )


@app.post("/generations/{id}")
def get(id: int):
    return generation_preview(id)


@app.post("/")
def post(prompt: str):
    id = len(generations)
    generate_and_save(prompt, id)
    generations.append(prompt)
    clear_input = Input(
        id="new-prompt", name="prompt", placeholder="Enter a prompt", hx_swap_oob="true"
    )
    return generation_preview(id), clear_input


@threaded
def generate_and_save(prompt, id):
    output = client.run(
        "playgroundai/playground-v2.5-1024px-aesthetic:a45f82a1382bed5c7aeb861dac7c7d191b0fdf74d8d57c4a0e6ed7d4d0bf7d24",
        input={
            "width": 1024,
            "height": 1024,
            "prompt": prompt,
            "scheduler": "DPMSolver++",
            "num_outputs": 1,
            "guidance_scale": 3,
            "apply_watermark": True,
            "negative_prompt": "ugly, deformed, noisy, blurry, distorted",
            "prompt_strength": 0.8,
            "num_inference_steps": 25,
        },
    )
    Image.open(requests.get(output[0], stream=True).raw).save(f"{folder}/{id}.png")
    return True


serve()
