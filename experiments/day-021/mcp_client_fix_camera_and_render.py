import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

JAPANESE_INSTRUCTION = "低ポリゴンのダンジョンシーンを作って。石の壁で囲まれた部屋と、中央に松明を1本置いて、カメラで部屋全体が見えるようにレンダリングして。"

FIX_CAMERA_CODE = r'''
import bpy, math

cam = bpy.data.objects.get("RoomCamera")
cam.location = (0, -7.0, 11.0)
cam.rotation_euler = (0, 0, 0)
cam.data.lens = 28

target = bpy.data.objects.get("AimTarget")
if target is None:
    target = bpy.data.objects.new("AimTarget", None)
    bpy.context.collection.objects.link(target)
target.location = (0, 0, 1.0)

for c in list(cam.constraints):
    cam.constraints.remove(c)
con = cam.constraints.new(type='TRACK_TO')
con.target = target
con.track_axis = 'TRACK_NEGATIVE_Z'
con.up_axis = 'UP_Y'

bpy.context.view_layer.update()

light = bpy.data.objects.get("Torch_Flame_Light")
if light:
    light.data.energy = 200

sun = bpy.data.objects.get("FillSun")
if sun is None:
    bpy.ops.object.light_add(type='SUN', location=(0, -4, 6))
    sun = bpy.context.active_object
    sun.name = "FillSun"
    sun.data.energy = 1.5
    sun.rotation_euler = (math.radians(45), 0, math.radians(20))

scene = bpy.context.scene
scene.camera = cam
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.filepath = "/home/user/ai-100days/experiments/day-021/after.png"
bpy.ops.render.render(write_still=True)

cam_info = {
    "cam_loc": tuple(cam.location),
    "cam_rot_euler_final": tuple(cam.matrix_world.to_euler()),
}
print("AFTER_RENDER_FIXED2:" + str(cam_info))
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
            exec_result = await session.call_tool(
                "execute_blender_code",
                {"code": FIX_CAMERA_CODE, "user_prompt": JAPANESE_INSTRUCTION},
            )
            for c in exec_result.content:
                print(getattr(c, "text", c))


if __name__ == "__main__":
    asyncio.run(main())
