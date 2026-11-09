-- Local pre-check of the documented Marketplace rules for RIGID accessories, run on a rig wearing the set
-- (use an UNSCALED body: R6 or classic R15 from wear_crystal_vanguard.lua). Studio MCP `execute_luau` (Edit) or command bar.
-- This is NOT Roblox's own validator: that one runs in Save to Roblox > Avatar Asset (the paid upload flow).
-- Rules from create.roblox.com/docs/avatar/rigid-accessories/specifications (read 2026-11-09):
--   box per type measured in the attachment frame (W=X, H=Y, D=Z, front = -Z), <= 4000 triangles, watertight single mesh,
--   texture <= 2048x2048, Material Plastic, Transparency 0, no extra objects in the Accessory.
-- RIG: name of an unscaled rig wearing the set. To make one: in your wear script (e.g. wear_crystal_vanguard.lua) set
-- CONFIG.name = "TEST_R6" and CONFIG.rigType = Enum.HumanoidRigType.R6, run it, then run this file. Change RIG for other names.
local RIG = "TEST_R6"
-- {W, H, D, up, down, front, behind}; up/down/front/behind only for the off-centre entries (nil = centred)
local LIMITS = {
  Classic = {
    Hat = {3, 4, 3}, Hair = {3, 5, 3.5, 2, 3, 1.5, 2}, Face = {3, 2, 2}, Neck = {3, 3, 2}, Shoulder = {3, 3, 3},
    Front = {3, 3, 3}, Back = {10, 7, 4.5, nil, nil, 1.5, 3}, Waist = {4, 3.5, 7, 1.5, 2},
  },
  Normal = {
    Hat = {1.87, 2.5, 1.87}, Hair = {1.87, 3.12, 2.18, 1.25, 1.875, 0.9375, 1.25}, Face = {1.87, 1.25, 1.25},
    Neck = {2.95, 3.68, 2.16}, Shoulder = {2.67, 4.40, 3.09}, Front = {2.95, 3.68, 3.24},
    Back = {9.86, 8.59, 4.87, nil, nil, 1.623, 3.246}, Waist = {3.94, 4.29, 7.57, 1.842, 2.457},
  },
  Slender = {
    Hat = {1.78, 2.5, 1.78}, Hair = {1.78, 3.12, 2.08, 1.25, 1.875, 0.892, 1.189}  -- page prints 1.892 (typo: front+behind = 2.08), Face = {1.78, 1.25, 1.18},
    Neck = {2.59, 3.39, 1.92}, Shoulder = {2.37, 3.96, 2.75}, Front = {2.59, 3.39, 2.88},
    Back = {8.64, 7.91, 4.32, nil, nil, 1.443, 2.886}, Waist = {3.76, 3.29, 6.73, 1.414, 1.885},
  },
}
local TYPE_OF = {  -- attachment name -> accessory types to test
  HatAttachment = {"Hat", "Hair"}, HairAttachment = {"Hair"}, FaceFrontAttachment = {"Face"},
  NeckAttachment = {"Neck"}, RightShoulderAttachment = {"Shoulder"}, LeftShoulderAttachment = {"Shoulder"},
  BodyFrontAttachment = {"Front"}, BodyBackAttachment = {"Back"},
  WaistBackAttachment = {"Waist"}, WaistFrontAttachment = {"Waist"}, WaistCenterAttachment = {"Waist"},
}
local AS = game:GetService("AssetService")
local function fits(lim, lo, hi)  -- lo/hi: Vector3 min/max of the mesh box in the attachment frame
  local size = hi - lo; local bad = {}
  if size.X > lim[1] + 1e-3 then table.insert(bad, string.format("W %.2f>%.2f", size.X, lim[1])) end
  if lim[4] then
    if hi.Y > lim[4] then table.insert(bad, string.format("up %.2f>%.2f", hi.Y, lim[4])) end
    if -lo.Y > lim[5] then table.insert(bad, string.format("down %.2f>%.2f", -lo.Y, lim[5])) end
  elseif math.max(hi.Y, -lo.Y) > lim[2] / 2 then table.insert(bad, string.format("H half %.2f>%.2f", math.max(hi.Y, -lo.Y), lim[2] / 2)) end
  if lim[6] then
    if -lo.Z > lim[6] then table.insert(bad, string.format("front %.2f>%.2f", -lo.Z, lim[6])) end
    if hi.Z > lim[7] then table.insert(bad, string.format("behind %.2f>%.2f", hi.Z, lim[7])) end
  elseif math.max(hi.Z, -lo.Z) > lim[3] / 2 then table.insert(bad, string.format("D half %.2f>%.2f", math.max(hi.Z, -lo.Z), lim[3] / 2)) end
  if math.max(hi.X, -lo.X) > lim[1] / 2 + 1e-3 then table.insert(bad, string.format("W half %.2f>%.2f", math.max(hi.X, -lo.X), lim[1] / 2)) end
  return #bad == 0 and "ok" or table.concat(bad, ", ")
end
local out = {}
for _, acc in ipairs(workspace[RIG]:GetChildren()) do
  if acc:IsA("Accessory") then
    local h = acc:FindFirstChild("Handle"); local att = h:FindFirstChildWhichIsA("Attachment")
    local lines = {acc.Name}
    -- mesh box in the attachment frame (attachment has no rotation, so only a shift)
    local c = att.CFrame:PointToObjectSpace(Vector3.zero)
    local lo, hi = c - h.Size / 2, c + h.Size / 2
    table.insert(lines, string.format("  box W %.2f H %.2f D %.2f | up %.2f down %.2f front %.2f behind %.2f",
      h.Size.X, h.Size.Y, h.Size.Z, hi.Y, -lo.Y, -lo.Z, hi.Z))
    for _, ty in ipairs(TYPE_OF[att.Name] or {}) do
      local r = {}
      for _, scale in ipairs({"Classic", "Normal", "Slender"}) do table.insert(r, scale .. ": " .. fits(LIMITS[scale][ty], lo, hi)) end
      table.insert(lines, "  " .. ty .. " -> " .. table.concat(r, " | "))
    end
    -- triangles + watertight (every edge used by exactly 2 faces)
    local ok, em = pcall(function() return AS:CreateEditableMeshAsync(Content.fromUri(h.MeshId)) end)
    if ok and em then
      local faces = em:GetFaces(); local edges, open = {}, 0
      for _, f in ipairs(faces) do
        local v = em:GetFaceVertices(f)
        for i = 1, #v do
          local a, b = v[i], v[i % #v + 1]
          local pa, pb = em:GetPosition(a), em:GetPosition(b)
          local ka = string.format("%.4f,%.4f,%.4f", pa.X, pa.Y, pa.Z); local kb = string.format("%.4f,%.4f,%.4f", pb.X, pb.Y, pb.Z)
          local k = ka < kb and (ka .. "|" .. kb) or (kb .. "|" .. ka)
          edges[k] = (edges[k] or 0) + 1
        end
      end
      for _, n in pairs(edges) do if n ~= 2 then open += 1 end end
      table.insert(lines, string.format("  tris %d (%s), edges not shared by exactly 2 faces: %d (%s)", #faces,
        #faces <= 4000 and "ok" or "OVER 4000", open, open == 0 and "watertight" or "NOT watertight"))
    else table.insert(lines, "  mesh read failed: " .. tostring(em)) end
    local okI, ei = pcall(function() return AS:CreateEditableImageAsync(Content.fromUri(h.TextureID)) end)
    if okI and ei then table.insert(lines, string.format("  texture %dx%d (%s)", ei.Size.X, ei.Size.Y,
      (ei.Size.X <= 2048 and ei.Size.Y <= 2048) and "ok" or "OVER 2048")) else table.insert(lines, "  texture read failed: " .. tostring(ei)) end
    local extra = {}
    for _, d in ipairs(acc:GetDescendants()) do
      if not (d == h or d:IsA("Attachment") or d:IsA("Weld") or d:IsA("WrapLayer") or d:IsA("SurfaceAppearance")) then table.insert(extra, d.ClassName .. ":" .. d.Name) end
    end
    table.insert(lines, string.format("  material %s, transparency %g, extra objects: %s", h.Material.Name, h.Transparency,
      #extra == 0 and "none" or table.concat(extra, ",")))
    table.insert(out, table.concat(lines, "\n"))
  end
end
local s = table.concat(out, "\n")
print(s)
return s
