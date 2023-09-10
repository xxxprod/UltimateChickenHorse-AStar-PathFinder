using HarmonyLib;
using UnityEngine;

namespace UCHBot.GlobalMods.Patches;

[HarmonyPatch(typeof(Application))]
public static class ApplicationPatches
{
    [HarmonyPostfix]
    [HarmonyPatch(nameof(Application.persistentDataPath), MethodType.Getter)]
    public static void PostFix1(out string __result)
    {
        __result = Environment.CurrentDirectory + "\\..\\UCH-PersistentData";
    }
}