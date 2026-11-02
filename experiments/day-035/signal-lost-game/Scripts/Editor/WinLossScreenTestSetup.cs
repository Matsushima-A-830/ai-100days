#if UNITY_EDITOR
using SignalLost.DebugTools;
using SignalLost.UI;
using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;

namespace SignalLost.EditorTools
{
    /// <summary>
    /// Throwaway editor tooling for Story 002 (win/loss screen) manual
    /// verification. NOT part of any story's scope — builds the GameObjects
    /// needed to see <see cref="WinLossScreen"/> render in Play mode, so a
    /// developer can screenshot it for the story's required evidence.
    /// </summary>
    public static class WinLossScreenTestSetup
    {
        private const string PanelSettingsPath = "Assets/UI/TestPanelSettings.asset";
        private const string UxmlPath = "Assets/UI/WinLossScreen.uxml";

        [MenuItem("Signal Lost/Setup WinLoss Test Scene")]
        public static void SetupScene()
        {
            var panelSettings = GetOrCreatePanelSettings();
            var uxml = AssetDatabase.LoadAssetAtPath<VisualTreeAsset>(UxmlPath);

            if (uxml == null)
            {
                Debug.LogError($"WinLossScreenTestSetup: could not load UXML at {UxmlPath}.");
                return;
            }

            var screenObject = new GameObject("WinLossScreenTest");
            var uiDocument = screenObject.AddComponent<UIDocument>();
            uiDocument.panelSettings = panelSettings;
            uiDocument.visualTreeAsset = uxml;
            screenObject.AddComponent<WinLossScreen>();

            var harnessObject = new GameObject("WinLossScreenTestHarness");
            harnessObject.AddComponent<WinLossScreenTestHarness>();

            Selection.activeGameObject = screenObject;
            Debug.Log("WinLossScreenTestSetup: scene objects created. Enter Play mode, then press W (win) or L (loss).");
        }

        private static PanelSettings GetOrCreatePanelSettings()
        {
            var existing = AssetDatabase.LoadAssetAtPath<PanelSettings>(PanelSettingsPath);
            if (existing != null)
            {
                return existing;
            }

            var settings = ScriptableObject.CreateInstance<PanelSettings>();
            AssetDatabase.CreateAsset(settings, PanelSettingsPath);
            AssetDatabase.SaveAssets();
            return settings;
        }
    }
}
#endif
