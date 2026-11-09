-- Showroom experience (track 4: experiences). Builds a small showroom around rigs that already wear a set, in EDIT mode.
-- Run with the Studio MCP `execute_luau` (datamodel Edit) or paste into the command bar, AFTER the wear scripts
-- (docs/studio/wear_crystal_vanguard.lua -> "CVRig", docs/studio/wear_tidewatch.lua -> "TWRig"). Use freshly worn rigs:
-- an edit-mode animation pose (docs/studio/pose_anim.lua) cannot be cleared from here, part CFrames keep the pose.
-- What it makes (idempotent: an existing "Showroom" folder and "ShowroomServer" script are replaced):
--   * one plinth per display rig with a "Try on" ProximityPrompt and a name sign; rigs anchored on top, slow turntable
--   * dusk lighting with Technology Future + Bloom so SurfaceAppearance emissive crystals glow
--   * ServerScriptService.ShowroomServer: turntable + try-on (copies the display rig's accessories, shirt, pants and face
--     plate onto the player's character). No InsertService at runtime: it clones what the display rig wears.
-- Private assets only load in places owned by the uploader (test in Studio first; never publish without the owner).
local DISPLAYS = {
  {rig = "CVRig", label = "Crystal Vanguard", position = Vector3.new(0, 0, 0)},
  {rig = "TWRig", label = "Tidewatch Warden", position = Vector3.new(-8, 0, 0)},
}
local PLINTH_H = 1.2

local SSS, Lighting = game:GetService("ServerScriptService"), game:GetService("Lighting")
for _, o in ipairs({workspace:FindFirstChild("Showroom"), SSS:FindFirstChild("ShowroomServer")}) do if o then o.Parent = nil end end
local folder = Instance.new("Folder"); folder.Name = "Showroom"

local function part(props)
  local p = Instance.new("Part"); p.Anchored = true; p.TopSurface = Enum.SurfaceType.Smooth; p.BottomSurface = Enum.SurfaceType.Smooth
  for k, v in pairs(props) do p[k] = v end
  return p
end

-- floor + back wall with soft blue strips
part({Name = "Floor", Size = Vector3.new(40, 0.2, 24), Position = Vector3.new(-4, 0.1, 2), Color = Color3.fromRGB(28, 32, 48), Material = Enum.Material.Slate, Parent = folder})
part({Name = "Wall", Size = Vector3.new(40, 16, 1), Position = Vector3.new(-4, 8, 8), Color = Color3.fromRGB(22, 26, 40), Material = Enum.Material.SmoothPlastic, Parent = folder})
for k = -2, 2 do
  part({Name = "Strip", Size = Vector3.new(0.3, 12, 0.2), Position = Vector3.new(-4 + k * 7, 8, 7.4), Color = Color3.fromRGB(120, 200, 255), Material = Enum.Material.Neon, Parent = folder})
end

local plinths = Instance.new("Folder"); plinths.Name = "Plinths"; plinths.Parent = folder
for _, d in ipairs(DISPLAYS) do
  local rig = workspace:FindFirstChild(d.rig)
  if rig then
    local base = d.position
    local p = part({Name = d.rig .. "Plinth", Shape = Enum.PartType.Cylinder, Size = Vector3.new(PLINTH_H, 5, 5),
      CFrame = CFrame.new(base + Vector3.new(0, PLINTH_H / 2, 0)) * CFrame.Angles(0, 0, math.rad(90)),
      Color = Color3.fromRGB(46, 52, 74), Material = Enum.Material.Marble, Parent = plinths})
    part({Name = "Ring", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.14, 5.3, 5.3),   -- sunk: only a gold rim shows
      CFrame = CFrame.new(base + Vector3.new(0, PLINTH_H - 0.22, 0)) * CFrame.Angles(0, 0, math.rad(90)),
      Color = Color3.fromRGB(212, 175, 55), Material = Enum.Material.Metal, Parent = plinths})
    -- key light: spotlight above and in front of the plinth, aimed at the chest
    local lamp = part({Name = "Lamp", Size = Vector3.new(0.4, 0.4, 0.4), Transparency = 1, CanCollide = false,
      CFrame = CFrame.lookAt(base + Vector3.new(0, 10, -5), base + Vector3.new(0, 4, 0)), Parent = plinths})
    local sl = Instance.new("SpotLight"); sl.Face = Enum.NormalId.Front; sl.Angle = 55; sl.Range = 18; sl.Brightness = 4
    sl.Color = Color3.fromRGB(255, 244, 228); sl.Shadows = true; sl.Parent = lamp
    p:SetAttribute("Rig", d.rig)
    local prompt = Instance.new("ProximityPrompt"); prompt.ActionText = "Try on"; prompt.ObjectText = d.label
    prompt.KeyboardKeyCode = Enum.KeyCode.E; prompt.MaxActivationDistance = 10; prompt.RequiresLineOfSight = false; prompt.Parent = p
    -- name sign in front of the plinth
    local sign = part({Name = "Sign", Size = Vector3.new(3.4, 0.7, 0.1), CFrame = CFrame.new(base + Vector3.new(0, 0.75, -3.0)) * CFrame.Angles(math.rad(-15), 0, 0),
      Transparency = 1, CanCollide = false, Parent = plinths})
    local gui = Instance.new("SurfaceGui"); gui.Face = Enum.NormalId.Front; gui.Parent = sign
    local t = Instance.new("TextLabel"); t.Size = UDim2.fromScale(1, 1); t.BackgroundTransparency = 1; t.Text = d.label
    t.TextScaled = true; t.Font = Enum.Font.GothamBold; t.TextColor3 = Color3.fromRGB(235, 225, 190); t.Parent = gui
    -- stand the rig on the plinth: feet at the plinth top (HipHeight + half root height above it)
    local hum = rig:FindFirstChildOfClass("Humanoid"); local root = rig:FindFirstChild("HumanoidRootPart")
    local y = PLINTH_H + hum.HipHeight + root.Size.Y / 2
    root.Anchored = true; rig:PivotTo(CFrame.new(base + Vector3.new(0, y, 0)))
    rig:SetAttribute("ShowroomBase", base + Vector3.new(0, y, 0))
    -- clear any edit-time animation pose
    for _, m in ipairs(rig:GetDescendants()) do if m:IsA("Motor6D") then m.Transform = CFrame.new() end end
    local an = hum:FindFirstChildOfClass("Animator"); if an then for _, tr in ipairs(an:GetPlayingAnimationTracks()) do tr:Stop(0) end end
  end
end

-- spawn in front of the plinths
local spawn = workspace:FindFirstChildOfClass("SpawnLocation")
if spawn then spawn.CFrame = CFrame.new(-4, 0.6, -10); spawn.Transparency = 1; spawn.CanCollide = false
  local decal = spawn:FindFirstChildOfClass("Decal"); if decal then decal.Transparency = 1 end end
folder.Parent = workspace

-- lighting: dusk, Future technology, bloom so neon/emissive read as light
-- Technology is not writable from the Studio MCP / command-bar thread ("lacking capability RobloxScript"):
-- set Lighting.Technology = Future by hand in Properties if it is not already (new places default to Future/ShadowMap).
pcall(function() Lighting.Technology = Enum.Technology.Future end)
Lighting.ClockTime = 17.4; Lighting.Brightness = 2
Lighting.Ambient = Color3.fromRGB(80, 86, 120); Lighting.OutdoorAmbient = Color3.fromRGB(110, 120, 160)
for _, n in ipairs({"ShowroomBloom", "ShowroomCC"}) do local o = Lighting:FindFirstChild(n); if o then o.Parent = nil end end
local bloom = Instance.new("BloomEffect"); bloom.Name = "ShowroomBloom"; bloom.Intensity = 0.6; bloom.Size = 28; bloom.Threshold = 0.95; bloom.Parent = Lighting
local cc = Instance.new("ColorCorrectionEffect"); cc.Name = "ShowroomCC"; cc.Contrast = 0.08; cc.Saturation = 0.08; cc.Parent = Lighting

-- server logic
local s = Instance.new("Script"); s.Name = "ShowroomServer"
s.Source = [==[
-- Showroom: turntable + "Try on" (generated by experiences/showroom/build_showroom.lua)
local RunService = game:GetService("RunService")
local plinths = workspace:WaitForChild("Showroom"):WaitForChild("Plinths")

local function rigFor(plinth) return workspace:FindFirstChild(plinth:GetAttribute("Rig") or "") end

local function tryOn(player, rig)
  local char = player.Character; local hum = char and char:FindFirstChildOfClass("Humanoid")
  if not (hum and rig) then return end
  hum:RemoveAccessories()
  for _, c in ipairs(char:GetChildren()) do
    if c:IsA("Shirt") or c:IsA("Pants") or c.Name == "FacePlate" then c:Destroy() end
  end
  for _, c in ipairs(rig:GetChildren()) do
    if c:IsA("Accessory") then
      local acc = c:Clone()
      for _, w in ipairs(acc:GetDescendants()) do if w:IsA("JointInstance") or w:IsA("WeldConstraint") then w:Destroy() end end
      hum:AddAccessory(acc)
    elseif c:IsA("Shirt") or c:IsA("Pants") then
      c:Clone().Parent = char
    end
  end
  local plate = rig:FindFirstChild("FacePlate"); local head = char:FindFirstChild("Head")
  if plate and head then
    if head:IsA("MeshPart") then head.TextureID = "" end
    local fp = plate:Clone(); for _, w in ipairs(fp:GetChildren()) do if w:IsA("WeldConstraint") then w:Destroy() end end
    fp.Anchored = false; fp.CFrame = head.CFrame * CFrame.new(0, 0, -head.Size.Z / 2 - 0.03)
    local w = Instance.new("WeldConstraint"); w.Part0 = head; w.Part1 = fp; w.Parent = fp; fp.Parent = char
  end
  print("[Showroom] " .. player.Name .. " tried on " .. rig.Name)
end

for _, p in ipairs(plinths:GetChildren()) do
  local prompt = p:FindFirstChildOfClass("ProximityPrompt")
  if prompt then prompt.Triggered:Connect(function(player) tryOn(player, rigFor(p)) end) end
end
-- automation hook: Studio MCP / plugin code runs in another VM (no shared _G) and cannot press ProximityPrompts,
-- so tests call ServerScriptService.ShowroomServer.TryOn:Invoke(player, "CVRig") from the Server datamodel
local bf = Instance.new("BindableFunction"); bf.Name = "TryOn"
bf.OnInvoke = function(player, rigName) tryOn(player, workspace:FindFirstChild(rigName)); return true end
bf.Parent = script

local t0 = os.clock()
RunService.Heartbeat:Connect(function()
  local a = (os.clock() - t0) * 0.35
  for _, p in ipairs(plinths:GetChildren()) do
    local rig = rigFor(p); local base = rig and rig:GetAttribute("ShowroomBase")
    if base then rig:PivotTo(CFrame.new(base) * CFrame.Angles(0, a, 0)) end
  end
end)
]==]
s.Parent = SSS
return "showroom built: " .. #plinths:GetChildren() .. " plinth parts (set Lighting.Technology = Future by hand if needed)"
