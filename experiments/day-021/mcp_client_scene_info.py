import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

JAPANESE_INSTRUCTION = "低ポリゴンのダンジョンシーンを作って。石の壁で囲まれた部屋と、中央に松明を1本置いて。"

BLENDER_CODE = r'''
import bpy, math

# clear default scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# room: 4 low-poly stone walls using cubes, floor, and a torch (cone + small light)
wall_specs = [
    ("Wall_North", (0, 3, 1.5), (3, 0.2, 1.5)),
    ("Wall_South", (0, -3, 1.5), (3, 0.2, 1.5)),
    ("Wall_East", (3, 0, 1.5), (0.2, 3, 1.5)),
    ("Wall_West", (-3, 0, 1.5), (0.2, 3, 1.5)),
]
stone_mat = bpy.data.materials.new(name="StoneMat")
stone_mat.diffuse_color = (0.35, 0.33, 0.30, 1.0)

for name, loc, scale in wall_specs:
    bpy.ops.mesh.primitive_cube_add(location=loc)
    wall = bpy.context.active_object
    wall.name = name
    wall.scale = scale
    wall.data.materials.append(stone_mat)

bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
floor_mat = bpy.data.materials.new(name="FloorMat")
floor_mat.diffuse_color = (0.2, 0.18, 0.16, 1.0)
floor.data.materials.append(floor_mat)

# torch: cone handle + small point light at center of the room
bpy.ops.mesh.primitive_cone_add(radius1=0.05, depth=1.0, location=(0, 0, 0.5))
torch = bpy.context.active_object
torch.name = "Torch_Handle"
torch_mat = bpy.data.materials.new(name="TorchMat")
torch_mat.diffuse_color = (0.25, 0.15, 0.05, 1.0)
torch.data.materials.append(torch_mat)

bpy.ops.object.light_add(type='POINT', location=(0, 0, 1.1))
flame_light = bpy.context.active_object
flame_light.name = "Torch_Flame_Light"
flame_light.data.energy = 400
flame_light.data.color = (1.0, 0.55, 0.15)

result = {
    "object_count": len(bpy.data.objects),
    "object_names": sorted(o.name for o in bpy.data.objects),
}
print("SCENE_BUILD_RESULT:" + str(result))
'''


async def main():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "mcp-for-blender"],
        cwd="/tmp/claude-0/-home-user-ai-100days/58be72ad-8476-5973-a506-77a61791716d/scratchpad/day021/mcp-for-blender",
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = sorted(t.name for t in tools.tools)
            print("AVAILABLE_TOOLS:", tool_names)

            before = await session.call_tool("get_scene_info", {"user_prompt": JAPANESE_INSTRUCTION})
            print("\n--- BEFORE get_scene_info ---")
            for c in before.content:
                print(getattr(c, "text", c))

            exec_result = await session.call_tool(
                "execute_blender_code",
                {"code": BLENDER_CODE, "user_prompt": JAPANESE_INSTRUCTION},
            )
            print("\n--- execute_blender_code result ---")
            for c in exec_result.content:
                print(getattr(c, "text", c))

            after = await session.call_tool("get_scene_info", {"user_prompt": JAPANESE_INSTRUCTION})
            print("\n--- AFTER get_scene_info ---")
            for c in after.content:
                print(getattr(c, "text", c))


if __name__ == "__main__":
    asyncio.run(main())
