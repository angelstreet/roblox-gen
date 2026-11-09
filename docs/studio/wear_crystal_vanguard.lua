-- Paste into Roblox Studio's command bar (one go) and press Run. Wears the Crystal Vanguard r7 set on a new R15 rig.
-- Asset IDs are private test uploads of the repo owner's account (only that account can load them); re-upload with
-- examples/tidewatch-warden/upload_assets.py under your own account and replace the IDs.
local IS, P = game:GetService("InsertService"), game:GetService("Players")
local function img(decalId) local m = IS:LoadAsset(decalId); local d = m:FindFirstChildWhichIsA("Decal", true); local t = d.Texture; m.Parent = nil; return t end
local function mesh(id) local m = IS:LoadAsset(id); local mp = m:FindFirstChildWhichIsA("MeshPart", true); mp.Parent = nil; m.Parent = nil; return mp end
local rig = P:CreateHumanoidModelFromDescription(Instance.new("HumanoidDescription"), Enum.HumanoidRigType.R15)
rig.Name = "CVRig"; rig.Parent = workspace; rig:PivotTo(CFrame.new(0, 5, 0))
for _, p in ipairs(rig:GetChildren()) do if p:IsA("BasePart") then p.Color = Color3.fromRGB(234, 184, 146) end end
local sh = Instance.new("Shirt"); sh.ShirtTemplate = img(73359961877284); sh.Parent = rig
local pa = Instance.new("Pants"); pa.PantsTemplate = img(95673074413632); pa.Parent = rig
local items = {  -- {mesh FBX id, texture Decal id, attachment}
  {103085628642625, 134139041954755, "HatAttachment"},            -- crown + hair
  {101325492073648, 99098738461939,  "RightShoulderAttachment"},  -- pauldron R
  {91788567476911,  99098738461939,  "LeftShoulderAttachment"},   -- pauldron L (shares the R texture)
  {129063076131913, 94334699278170,  "BodyBackAttachment"},       -- cape
  {89732359696876,  139046121543345, "NeckAttachment"},           -- scarf
  {127694122813832, 83328938307996,  "WaistBackAttachment"},      -- sword
}
for _, it in ipairs(items) do
  local mp = mesh(it[1]); mp.Name = "Handle"; mp.TextureID = img(it[2])
  local a = Instance.new("Attachment"); a.Name = it[3]; a.CFrame = CFrame.new(mp.PivotOffset.Position); a.Parent = mp  -- position only, no rotation
  local acc = Instance.new("Accessory"); acc.Name = it[3]; mp.Parent = acc
  rig.Humanoid:AddAccessory(acc)
  print(it[3], "size", mp.Size, "tris-check via MeshPart; pivot", mp.PivotOffset.Position)
end
