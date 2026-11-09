-- Wears the Ember Warden set (cold Sonnet test, starter/ember-warden) on a new rig. Paste into Roblox Studio's command bar and Run, or send it with the
-- Studio MCP `execute_luau` tool (datamodel Edit). Edit the CONFIG block to test other bodies.
-- Asset IDs are private test uploads of the repo owner's account (only that account can load them); re-upload with
-- scripts/upload_assets.py under your own account and replace the IDs (README "Make your own set" steps 5-6).
local CONFIG = {
  name = "EWRig",                       -- rig name in workspace (an existing rig with this name is removed first)
  rigType = Enum.HumanoidRigType.R15,   -- or Enum.HumanoidRigType.R6
  position = Vector3.new(0, 5, 0),
  -- HumanoidDescription scales: classic blocky = defaults. Rthro Normal: BodyTypeScale 1, ProportionScale 0;
  -- Rthro Slender: BodyTypeScale 1, ProportionScale 1 (R15 only).
  scales = { HeightScale = 1, WidthScale = 1, DepthScale = 1, HeadScale = 1, BodyTypeScale = 0, ProportionScale = 0 },
  glow = true,          -- SurfaceAppearance with the emissive masks (Marketplace: emissive items cost 500 Robux to upload)
  glowStrength = 1.5,
  glowTint = Color3.fromRGB(255, 130, 40),
  face = true,          -- face decal on the head (display only, classic faces are not UGC)
}

local IS, P = game:GetService("InsertService"), game:GetService("Players")
local old = workspace:FindFirstChild(CONFIG.name); if old then old.Parent = nil end
local function img(decalId) local m = IS:LoadAsset(decalId); local d = m:FindFirstChildWhichIsA("Decal", true); local t = d.Texture; m.Parent = nil; return t end
local function mesh(id) local m = IS:LoadAsset(id); local mp = m:FindFirstChildWhichIsA("MeshPart", true); mp.Parent = nil; m.Parent = nil; return mp end
local desc = Instance.new("HumanoidDescription")
for k, v in pairs(CONFIG.scales) do desc[k] = v end
local rig = P:CreateHumanoidModelFromDescription(desc, CONFIG.rigType)
rig.Name = CONFIG.name; rig.Parent = workspace; rig:PivotTo(CFrame.new(CONFIG.position))
for _, p in ipairs(rig:GetChildren()) do if p:IsA("BasePart") then p.Color = Color3.fromRGB(234, 184, 146) end end
local sh = Instance.new("Shirt"); sh.ShirtTemplate = img(70622572324435); sh.Parent = rig
local pa = Instance.new("Pants"); pa.PantsTemplate = img(99183828750535); pa.Parent = rig
if CONFIG.face then
  -- The default R15 head is a dynamic MeshPart head: a Decal on it maps into the mesh UVs (lands as a speck) and the default
  -- face is painted in its TextureID. So: clear that texture and put the face on a thin plate welded in front of the head.
  -- The plate must be Transparency 0.98, not 1 (decals on fully transparent parts are not drawn).
  local h = rig.Head; h.TextureID = ""; local old = h:FindFirstChild("face"); if old then old.Parent = nil end
  local plate = Instance.new("Part"); plate.Name = "FacePlate"; plate.Size = Vector3.new(h.Size.X * 0.98, h.Size.Y * 0.98, 0.05)
  plate.Transparency = 0.98; plate.CanCollide = false; plate.CanQuery = false; plate.Massless = true
  plate.CFrame = h.CFrame * CFrame.new(0, 0, -h.Size.Z / 2 - 0.03)
  local f = Instance.new("Decal"); f.Name = "face"; f.Face = Enum.NormalId.Front; f.Texture = img(120639939436489); f.Parent = plate
  local w = Instance.new("WeldConstraint"); w.Part0 = h; w.Part1 = plate; w.Parent = plate; plate.Parent = rig
end
local items = {  -- {mesh FBX id, texture Decal id, attachment, emissive mask Decal id}  (private uploads 2026-11-09)
  {124056084918864, 75582945847455,  "HatAttachment",           113375561389228},  -- ember helm + flame locks
  {110327161617209, 109314235261338, "RightShoulderAttachment", 106425827505689},  -- rock pauldron R
  {92588693330157,  109314235261338, "LeftShoulderAttachment",  106425827505689},  -- rock pauldron L (shares the R texture)
  {77174756343534,  117741314318999, "BodyBackAttachment",      136893595580275},  -- tattered cape
  {91500868463454,  75364604100127,  "NeckAttachment",          80508769972507},   -- obsidian collar
  {72900513581505,  111014400624896, "WaistBackAttachment",     74372438835831},   -- molten axe
}
local log = {}
for _, it in ipairs(items) do
  local mp = mesh(it[1]); mp.Name = "Handle"; mp.TextureID = img(it[2])
  if CONFIG.glow then
    local sa = Instance.new("SurfaceAppearance"); sa.ColorMapContent = Content.fromUri(img(it[2]))
    sa.EmissiveMaskContent = Content.fromUri(img(it[4])); sa.EmissiveStrength = CONFIG.glowStrength; sa.EmissiveTint = CONFIG.glowTint; sa.Parent = mp
  end
  local a = Instance.new("Attachment"); a.Name = it[3]; a.CFrame = CFrame.new(mp.PivotOffset.Position); a.Parent = mp  -- position only, no rotation
  local acc = Instance.new("Accessory"); acc.Name = it[3]; mp.Parent = acc
  rig.Humanoid:AddAccessory(acc)
  table.insert(log, string.format("%s size %.2f x %.2f x %.2f", it[3], mp.Size.X, mp.Size.Y, mp.Size.Z))
end
print(table.concat(log, "\n"))
return table.concat(log, "\n")
