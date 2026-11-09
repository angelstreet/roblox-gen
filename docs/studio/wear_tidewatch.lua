-- Wears the Tidewatch Warden v5 (r4 cape + skirt) set on a new rig. Paste into Roblox Studio's command bar and Run, or send it with the
-- Studio MCP `execute_luau` tool (datamodel Edit). Edit the CONFIG block to test other bodies.
-- Asset IDs are private test uploads of the repo owner's account (only that account can load them); re-upload with
-- scripts/upload_assets.py under your own account and replace the IDs (README "Make your own set" steps 5-6).
local CONFIG = {
  name = "TWRig",                       -- rig name in workspace (an existing rig with this name is removed first)
  rigType = Enum.HumanoidRigType.R15,   -- or Enum.HumanoidRigType.R6
  position = Vector3.new(-8, 5, 0),
  -- HumanoidDescription scales: classic blocky = defaults. Rthro Normal: BodyTypeScale 1, ProportionScale 0;
  -- Rthro Slender: BodyTypeScale 1, ProportionScale 1 (R15 only).
  scales = { HeightScale = 1, WidthScale = 1, DepthScale = 1, HeadScale = 1, BodyTypeScale = 0, ProportionScale = 0 },
  glow = false, face = false,           -- Tidewatch has no emissive masks / face decal yet
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
local sh = Instance.new("Shirt"); sh.ShirtTemplate = img(116898490125752); sh.Parent = rig
local pa = Instance.new("Pants"); pa.PantsTemplate = img(99844070548048); pa.Parent = rig
local items = {  -- {mesh FBX id, texture Decal id, attachment} (v5 ids from examples/tidewatch-warden/docs/HISTORY_v1-v4.md; r4 cape/skirt in README.md)
  {125983264677959, 110127265892794, "HatAttachment"},            -- Tidecrest Hood
  {134418525303305, 71445317143304,  "NeckAttachment"},           -- Tide Mantle
  {102873019853819, 100259474531047, "BodyBackAttachment"},       -- Warden Cape r4 (top tucked under the mantle)
  {124776217777333, 127618188419787, "RightShoulderAttachment"},  -- Tide Pauldron R
  {71062800685242,  127618188419787, "LeftShoulderAttachment"},   -- Tide Pauldron L
  {85906048945961,  101424587573912, "WaistFrontAttachment"},     -- Tidewatch Belt
  {104883722977485, 94014986753297,  "WaistCenterAttachment"},    -- Tidefall Skirt r4 (open-front tail skirt)
}
local log = {}
for _, it in ipairs(items) do
  local mp = mesh(it[1]); mp.Name = "Handle"; mp.TextureID = img(it[2])
  local a = Instance.new("Attachment"); a.Name = it[3]; a.CFrame = CFrame.new(mp.PivotOffset.Position); a.Parent = mp  -- position only, no rotation
  local acc = Instance.new("Accessory"); acc.Name = it[3]; mp.Parent = acc
  rig.Humanoid:AddAccessory(acc)
  table.insert(log, string.format("%s size %.2f x %.2f x %.2f", it[3], mp.Size.X, mp.Size.Y, mp.Size.Z))
end
print(table.concat(log, "\n"))
return table.concat(log, "\n")
