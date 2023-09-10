using System.Collections;
using UnityEngine;

namespace UCHBot.Shared.Modules
{
    public static class TreeHouseLoaderModule
    {
        public static void LoadTreeHouse(GameState.GameMode gameMode)
        {
            GameState gameState = GameState.GetInstance();
            KeyboardInput keyboard = gameState.Keyboard;

            UCHTools.Log("Start loading tree house scene");

            GameObject mainMenuControl = GameObject.Find(nameof(MainMenuControl));
            MainMenuControl menuControl = mainMenuControl.GetComponent<MainMenuControl>();
            menuControl.JoinControllerToMainMenu(keyboard, true);

            LoadingInterstitialSplash splash = LoadingInterstitialSplash.Instance;
            GameSettings gameSettings = GameSettings.GetInstance();
            gameSettings.StartAsHost = true;
            gameSettings.StartLocal = true;
            gameSettings.matchInfo = null;
            gameSettings.GameMode = gameMode;
            LobbyManagerManager.Instance.StartCoroutine(FadeOutToLoad());
            splash.FadeOutAutomatically = false;
            splash.Skip();
            splash.FadeIn();

            UCHTools.Log("Finished loading tree house scene");
        }


        private static IEnumerator FadeOutToLoad()
        {
            LoadingInterstitialSplash splash = LoadingInterstitialSplash.Instance;
            bool autoFade = splash.FadeOutAutomatically;
            splash.FadeOutAutomatically = false;
            while (splash != null && splash.State != UISplashScreen.STATE.SHOW)
            {
                yield return null;
            }
            if (SaveSystemProtector.WaitingForSavefileOperations)
            {
                Debug.Log("Waiting for savefile operations to complete before starting...");
                while (SaveSystemProtector.WaitingForSavefileOperations)
                {
                    yield return null;
                }
            }
            IEnumerator gentleLoad = SceneManagerWrapper.DoGentleSceneLoad("TreeHouseLobby");
            while (gentleLoad.MoveNext())
            {
                yield return null;
            }
            splash.FadeOutAutomatically = autoFade;
        }
    }
}