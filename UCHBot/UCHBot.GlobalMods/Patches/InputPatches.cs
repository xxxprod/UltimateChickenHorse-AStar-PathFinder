using HarmonyLib;
using UCHBot.GlobalMods.Tools;
using UnityEngine;

namespace UCHBot.GlobalMods.Patches;

[HarmonyPatch(typeof(Input), nameof(Input.GetKey), typeof(KeyCode))]
public static class InputPatches
{
	public static bool Prefix(KeyCode key, ref bool __result)
	{
		bool? keyPressed = InputWrapper.GetKeyPressed(key);
		if (keyPressed.HasValue)
		{
			__result = keyPressed.Value;
			return false;
		}

		return true;
	}
}