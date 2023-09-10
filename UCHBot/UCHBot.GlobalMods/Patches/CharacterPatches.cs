using GameEvent;
using HarmonyLib;
using UCHBot.GlobalMods.Events;

namespace UCHBot.GlobalMods.Patches;

[HarmonyPatch(typeof(Character))]
public static class CharacterPatches
{
	[HarmonyPostfix]
	[HarmonyPatch("OnGoalTouched", MethodType.Normal)]
	public static void Prefix(Character __instance)
	{
		GameEventManager.SendEvent(new PlayerTouchedGoalEvent(__instance));
	}
}