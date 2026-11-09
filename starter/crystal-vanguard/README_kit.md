# Crystal Vanguard — Roblox Outfit & Sword POC Starter Kit

This package is an ORIGINAL visual concept and 3D sword blockout made for learning. It is NOT a ready-to-sell Roblox item. No finished shirt/pants UV maps, rigging, textures, certification, or Marketplace approval are included.

## Contents
- `crystal_vanguard_full_concept.png`: full AI-generated concept sheet
- `crystal_vanguard_weapon_reference.png`: enlarged crop of weapon orthographic concept (artist guide)
- `crystal_vanguard_avatar_reference.png`: avatar reference crop
- `crystal_vanguard_sword_blockout.glb`: actual editable, multi-part color-coded 3D sword blockout (the geometry, not AI image)
- `crystal_vanguard_sword_blockout.obj`: alternative mesh-only OBJ without guaranteed colors/materials
- `crystal_vanguard_prompts.md`: reusable prompts

## Blender (Mac) — 3D sword
1. Install Blender from blender.org and open Blender.
2. File > Import > glTF 2.0 (.glb/.gltf) > select `crystal_vanguard_sword_blockout.glb`.
3. Select individual parts in the Outliner. Inspect shape from front and side, edit shapes and topology, join objects only when you have finished adapting materials.
4. Make the geometry your own. Refine proportions, unwrap and texture it. This blockout uses flat per-part colors, not production textures, and has not been tested in Roblox Studio.
5. Export a compatible `.fbx` or `.gltf` from Blender with proper scale and orientation.

## Roblox Studio — import and test
1. Open Studio > Home > Import. Import your `.fbx` or `.gltf` and check scale, orientation and material warnings.
2. If it is a WEARABLE back/waist accessory, use Avatar Setup / Accessory Fitting Tool to define and test correct attachment, then validate against current rigid accessory specs.
3. If it is a HANDHELD gameplay sword, use a Tool with a Handle and appropriate grip setup; this is a different pipeline and not inherently a Marketplace avatar accessory.
4. Test on an actual avatar. Do not publish or spend Robux until validated.

## Classic clothing
Get official Roblox shirt and pants templates from https://create.roblox.com/docs/avatar/classic-clothing . The concept infographic's UV sketches are only illustrative. Do not submit those images as classic clothing assets.

## Official Roblox guides
- https://create.roblox.com/docs/art/accessories/creating-rigid
- https://create.roblox.com/docs/avatar/rigid-accessories/import
- https://create.roblox.com/docs/avatar/classic-clothing
