# NavRakhshak Blender workflow

The repository now contains a local Blender builder at `v2/blender/navrakshak_scene.py`.

## Run it locally

1. Open Blender 5.x.
2. Open **Scripting** workspace.
3. Create a new text block and paste `navrakshak_scene.py`.
4. Click **Run Script**.
5. The script clears the default scene and builds the NavRakhshak maritime scene.
6. It saves `NavRakhshak_Cinematic_3D.blend`, exports `NavRakhshak_Cinematic_3D.glb`, and renders a preview beside the current `.blend` location.

The scene contains a stylized fishing vessel, dynamic ocean surface, radar animation, safety geofence, wake curves, navigation lights, cinematic camera movement, and a web-oriented GLB export.

## Website role

The production web experience uses Three.js for real-time interaction. Blender is used for higher-fidelity asset creation and cinematic renders; Firebase remains the live telemetry source.
