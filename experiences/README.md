# Experiences (stage 4)

Places and scripts that show or use the avatar sets. Built in Studio by an agent through the Studio MCP
(`execute_luau` in the Edit datamodel), tested in Play mode, judged by `screen_capture` screenshots.

| Experience | What it is | Status |
|---|---|---|
| `showroom/` | Dusk showroom: one marble plinth per set, slow turntable, spotlights + bloom so emissive crystals glow, "Try on" ProximityPrompt that dresses the player in the displayed set | built and tested 2026-11-09 (Studio Play, private assets) |

## Showroom: build and test (about 2 minutes)
1. Open any place in Studio (Baseplate). Studio's Home screen has no MCP tools.
2. Wear the sets on display rigs (the shipped wear scripts use the repo owner's private asset ids: on another account,
   re-upload with `scripts/upload_assets.py` and put your ids in each wear script's `items` table and its
   `Shirt`/`Pants`/face ids first, see README "Make your own set" step 6): run `docs/studio/wear_crystal_vanguard.lua` (rig `CVRig`) and
   `docs/studio/wear_tidewatch.lua` (rig `TWRig`). Use freshly worn rigs, not ones posed with `pose_anim.lua`.
3. Run `experiences/showroom/build_showroom.lua`. It replaces any earlier `Showroom` folder and `ShowroomServer` script.
4. Play. Walk to a plinth and press E ("Try on"). Server prints `[Showroom] <player> tried on <rig>`.
5. Automated check (Studio MCP, Server datamodel, during Play):
   `game.ServerScriptService.ShowroomServer.TryOn:Invoke(game.Players:GetPlayers()[1], "CVRig")`, then list the
   character's Accessory/Shirt/Pants children and take a `screen_capture`.

Screenshots: `showroom/shots/showroom.jpg` (edit view), `showroom/shots/play_tryon.jpg` (player wearing Crystal Vanguard in Play).

## Traps (verified 2026-11-09)
- `Lighting.Technology` cannot be read or written from the MCP / command-bar thread ("lacking capability RobloxScript"):
  the script wraps it in `pcall`; set it by hand in Properties if needed.
- MCP `user_keyboard_input` E presses and `ProximityPrompt:InputHoldBegin()` from the MCP Client datamodel did not trigger
  the prompt (the plugin thread is not the player's input). Use the `TryOn` BindableFunction for automated tests; a human
  press of E is still worth one manual check.
- `_G` is not shared between a server Script and MCP code (separate VMs): expose test hooks as Bindable objects.
- Decal ids are not image ids; the wear scripts resolve them with `InsertService:LoadAsset` in Edit mode, and the
  try-on clones what the display rig already wears, so no asset loading happens at runtime.
- Private assets load only in places owned by the uploader. Nothing here is published; publishing a place or selling
  anything needs the owner's explicit yes.

## Next experience ideas
Photo booth with poses (default emotes) and a camera path; a small obby that rewards trying the sets on.
