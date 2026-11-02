#if UNITY_EDITOR
using System.IO;
using SignalLost.Debris;
using SignalLost.Player;
using SignalLost.UI;
using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;

namespace SignalLost.EditorTools
{
    /// <summary>
    /// Throwaway editor tooling that builds the full playable scene — NOT
    /// part of any story's formal scope. Creates the four part-definition
    /// data assets and the GameObjects wiring GameplayCoordinator,
    /// PlayerController, SalvageSpotView and WinLossScreen together.
    /// </summary>
    public static class SignalLostSceneSetup
    {
        private static readonly string[] SystemNames = { "Life Support", "Navigation", "Power Core", "Comms" };
        private static readonly Vector2[] SpotOffsets = { new Vector2(-4, 2), new Vector2(4, 2), new Vector2(-4, -2), new Vector2(4, -2) };

        private const string PartsFolder = "Assets/Data/Parts";
        private const string PanelSettingsPath = "Assets/UI/TestPanelSettings.asset";
        private const string UxmlPath = "Assets/UI/WinLossScreen.uxml";

        [MenuItem("Signal Lost/Setup Playable Scene")]
        public static void SetupScene()
        {
            var parts = GetOrCreatePartDefinitions();
            var panelSettings = GetOrCreatePanelSettings();
            var uxml = AssetDatabase.LoadAssetAtPath<VisualTreeAsset>(UxmlPath);

            if (uxml == null)
            {
                Debug.LogError($"SignalLostSceneSetup: could not load UXML at {UxmlPath}.");
                return;
            }

            SetupTopDownCamera();

            var winLossObject = new GameObject("WinLossScreen");
            var uiDocument = winLossObject.AddComponent<UIDocument>();
            uiDocument.panelSettings = panelSettings;
            uiDocument.visualTreeAsset = uxml;
            var winLossScreen = winLossObject.AddComponent<WinLossScreen>();

            var stationObject = new GameObject("Station");
            stationObject.transform.position = Vector3.zero;
            stationObject.transform.localScale = Vector3.one * 1.5f;
            var stationRenderer = stationObject.AddComponent<SpriteRenderer>();
            stationRenderer.sprite = CreateSquareSprite();
            stationRenderer.color = new Color(0.3f, 0.35f, 0.4f);

            for (int i = 0; i < parts.Length; i++)
            {
                var spotObject = new GameObject($"SalvageSpot_{SystemNames[i].Replace(" ", "")}");
                spotObject.transform.position = new Vector3(SpotOffsets[i].x, SpotOffsets[i].y, 0f);
                spotObject.AddComponent<SpriteRenderer>().sprite = CreateSquareSprite();

                var spotView = spotObject.AddComponent<SalvageSpotView>();
                var spotSerialized = new SerializedObject(spotView);
                spotSerialized.FindProperty("partDefinition").objectReferenceValue = parts[i];
                spotSerialized.ApplyModifiedPropertiesWithoutUndo();
            }

            var playerObject = new GameObject("Player");
            playerObject.transform.position = new Vector3(0f, -3f, 0f);
            playerObject.AddComponent<SpriteRenderer>();
            playerObject.AddComponent<PlayerController>();

            var coordinatorObject = new GameObject("GameplayCoordinator");
            var coordinator = coordinatorObject.AddComponent<GameplayCoordinator>();
            var coordinatorSerialized = new SerializedObject(coordinator);
            coordinatorSerialized.FindProperty("winLossScreen").objectReferenceValue = winLossScreen;
            coordinatorSerialized.FindProperty("stationTransform").objectReferenceValue = stationObject.transform;
            coordinatorSerialized.ApplyModifiedPropertiesWithoutUndo();

            Selection.activeGameObject = coordinatorObject;
            Debug.Log("SignalLostSceneSetup: scene built. Enter Play mode — WASD/arrows to move, Space to scan/collect/repair near a spot or the station.");
        }

        private static void SetupTopDownCamera()
        {
            var camera = Camera.main;
            if (camera == null)
            {
                var cameraObject = new GameObject("Main Camera");
                cameraObject.tag = "MainCamera";
                camera = cameraObject.AddComponent<Camera>();
            }

            camera.orthographic = true;
            camera.orthographicSize = 6f; // frames the +-4 / +-2 spot layout with margin
            camera.transform.position = new Vector3(0f, 0f, -10f);
            camera.transform.rotation = Quaternion.identity;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.05f, 0.05f, 0.08f);
        }

        private static PartDefinition[] GetOrCreatePartDefinitions()
        {
            EnsureFolder(PartsFolder);

            var parts = new PartDefinition[SystemNames.Length];
            for (int i = 0; i < SystemNames.Length; i++)
            {
                string systemName = SystemNames[i];
                string assetPath = $"{PartsFolder}/Part_{systemName.Replace(" ", "")}.asset";

                var existing = AssetDatabase.LoadAssetAtPath<PartDefinition>(assetPath);
                if (existing != null)
                {
                    parts[i] = existing;
                    continue;
                }

                var part = ScriptableObject.CreateInstance<PartDefinition>();
                var serialized = new SerializedObject(part);
                serialized.FindProperty("partId").stringValue = systemName.Replace(" ", "").ToLowerInvariant();
                serialized.FindProperty("displayName").stringValue = $"{systemName} Module";
                serialized.FindProperty("targetSystemName").stringValue = systemName;
                serialized.ApplyModifiedPropertiesWithoutUndo();

                AssetDatabase.CreateAsset(part, assetPath);
                parts[i] = part;
            }

            AssetDatabase.SaveAssets();
            return parts;
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

        private static Sprite CreateSquareSprite()
        {
            var texture = Texture2D.whiteTexture;
            return Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f), texture.width);
        }

        private static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path))
            {
                return;
            }

            string parent = Path.GetDirectoryName(path)?.Replace("\\", "/");
            string folderName = Path.GetFileName(path);

            if (!string.IsNullOrEmpty(parent) && !AssetDatabase.IsValidFolder(parent))
            {
                EnsureFolder(parent);
            }

            AssetDatabase.CreateFolder(parent, folderName);
        }
    }
}
#endif
