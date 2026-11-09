-- Wears the Crystal Vanguard set (r10) on a new rig. Paste into Roblox Studio's command bar and Run, or send it with the
-- Studio MCP `execute_luau` tool (datamodel Edit). Edit the CONFIG block to test other bodies.
-- Asset IDs are private test uploads of the repo owner's account (only that account can load them); re-upload with
-- scripts/upload_assets.py under your own account and replace the IDs (README "Make your own set" steps 5-6).
local CONFIG = {
  name = "CVRig",                       -- rig name in workspace (an existing rig with this name is removed first)
  rigType = Enum.HumanoidRigType.R15,   -- or Enum.HumanoidRigType.R6
  position = Vector3.new(0, 5, 0),
  -- HumanoidDescription scales: classic blocky = defaults. Rthro Normal: BodyTypeScale 1, ProportionScale 0;
  -- Rthro Slender: BodyTypeScale 1, ProportionScale 1 (R15 only).
  scales = { HeightScale = 1, WidthScale = 1, DepthScale = 1, HeadScale = 1, BodyTypeScale = 0, ProportionScale = 0 },
  glow = true,          -- SurfaceAppearance with the emissive masks (Marketplace: emissive items cost 500 Robux to upload)
  glowStrength = 1.5,
  glowTint = Color3.fromRGB(150, 215, 255),
  face = true,          -- r10 face decal on the head (display only, classic faces are not UGC)
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
local sh = Instance.new("Shirt"); sh.ShirtTemplate = img(137926471035226); sh.Parent = rig   -- r10 filigree shirt
local pa = Instance.new("Pants"); pa.PantsTemplate = img(128873900212839); pa.Parent = rig    -- r10 pants
if CONFIG.face then
  -- The default R15 head is a dynamic MeshPart head: a Decal on it maps into the mesh UVs (lands as a speck) and the default
  -- face is painted in its TextureID. So: clear that texture and put the face on a thin plate welded in front of the head.
  -- The plate must be Transparency 0.98, not 1 (decals on fully transparent parts are not drawn).
  local h = rig.Head; h.TextureID = ""; local old = h:FindFirstChild("face"); if old then old.Parent = nil end
  local plate = Instance.new("Part"); plate.Name = "FacePlate"; plate.Size = Vector3.new(h.Size.X * 0.98, h.Size.Y * 0.98, 0.05)
  plate.Transparency = 0.98; plate.CanCollide = false; plate.CanQuery = false; plate.Massless = true
  plate.CFrame = h.CFrame * CFrame.new(0, 0, -h.Size.Z / 2 - 0.03)
  local f = Instance.new("Decal"); f.Name = "face"; f.Face = Enum.NormalId.Front; f.Texture = img(135398494225892); f.Parent = plate
  local w = Instance.new("WeldConstraint"); w.Part0 = h; w.Part1 = plate; w.Parent = plate; plate.Parent = rig
end
local items = {  -- {mesh FBX id, texture Decal id, attachment, emissive mask Decal id}
  {129396675939617, 134139041954755, "HatAttachment",           125615870753450},   -- r10 crown + swept mane (Hair box, watertight)
  {101325492073648, 99098738461939,  "RightShoulderAttachment", 111757635753589},  -- pauldron R
  {91788567476911,  99098738461939,  "LeftShoulderAttachment",  111757635753589},  -- pauldron L (shares the R texture)
  {117927101168588, 84307101637758,  "BodyBackAttachment",      111720663243190},  -- r10 long flared cape
  {89732359696876,  139046121543345, "NeckAttachment",          90049570495779},   -- scarf
  {107433499133729, 83328938307996,  "WaistBackAttachment",     92076649973247},   -- r10 sword (lowered into the Waist box, watertight)
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
