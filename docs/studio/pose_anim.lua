-- Poses a rig at one frame of a default R15 animation in EDIT mode (no Play needed), then probes how far the legs
-- reach behind the torso. Run with the Studio MCP `execute_luau` (datamodel Edit) or the command bar.
-- Verified 2026-11-09: Animator:StepAnimations(dt) advances tracks in edit mode; tracks need ~1 s to load (Length 0).
-- Stopping a track does NOT restore the rest pose and part CFrames only refresh after a step: compare poses
-- against the idle animation, not against "no track".
-- Default R15 animation ids: idle 507766388, walk 507777826, run 507767714, jump 507765000, fall 507767968, climb 507765644.
_G.pose = function(rigName, id, t)
  local rig = workspace[rigName]
  local animator = rig.Humanoid:FindFirstChildOfClass("Animator") or Instance.new("Animator", rig.Humanoid)
  rig.HumanoidRootPart.Anchored = true
  for _, tr in ipairs(animator:GetPlayingAnimationTracks()) do tr:Stop(0) end
  for _, m in ipairs(rig:GetDescendants()) do if m:IsA("Motor6D") then m.Transform = CFrame.new() end end
  local a = Instance.new("Animation"); a.AnimationId = "rbxassetid://" .. id
  local tr = animator:LoadAnimation(a); tr:Play(0)
  local t0 = os.clock(); while tr.Length == 0 and os.clock() - t0 < 8 do task.wait(0.1) end
  animator:StepAnimations(t)
  return string.format("%d len %.2f tp %.2f", id, tr.Length, tr.TimePosition)
end
-- Max distance (studs) each leg part reaches behind the UpperTorso centre (+Z = back). The cape's back face is at about
-- +1.3 (centre 0.60 + half depth 0.72): larger values mean the leg can pass through the cape.
_G.probe = function(rigName)
  local rig = workspace[rigName]; local ut = rig.UpperTorso; local res = {}
  for _, n in ipairs({"LeftUpperLeg","RightUpperLeg","LeftLowerLeg","RightLowerLeg","LeftFoot","RightFoot"}) do
    local p = rig[n]; local maxz = -99
    for _, sx in ipairs({-1,1}) do for _, sy in ipairs({-1,1}) do for _, sz in ipairs({-1,1}) do
      local l = ut.CFrame:PointToObjectSpace(p.CFrame * Vector3.new(sx*p.Size.X/2, sy*p.Size.Y/2, sz*p.Size.Z/2))
      maxz = math.max(maxz, l.Z)
    end end end
    table.insert(res, string.format("%s %.2f", n, maxz))
  end
  return table.concat(res, "; ")
end
-- Example: return _G.pose("CVRig", 507767714, 0.37) .. " | " .. _G.probe("CVRig")   -- run, back-kick frame
return "pose/probe loaded"
