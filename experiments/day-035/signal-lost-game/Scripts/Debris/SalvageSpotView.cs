using UnityEngine;

namespace SignalLost.Debris
{
    /// <summary>
    /// Throwaway playable-scene visual for a <see cref="SalvageSpot"/> — NOT
    /// part of any story's formal scope. Owns the actual <see cref="SalvageSpot"/>
    /// model instance and colors a placeholder sprite by its current state so
    /// a player can see what to interact with. Built by
    /// `Signal Lost > Setup Playable Scene`.
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class SalvageSpotView : MonoBehaviour
    {
        private static readonly Color AvailableColor = new Color(0.5f, 0.5f, 0.55f);
        private static readonly Color RevealedColor = new Color(0.9f, 0.8f, 0.2f);
        private static readonly Color DepletedColor = new Color(0.15f, 0.15f, 0.15f);

        [SerializeField] private PartDefinition partDefinition;

        /// <summary>The domain model this view renders — the thing a player actually interacts with.</summary>
        public SalvageSpot Model { get; private set; }

        private SpriteRenderer spriteRenderer;

        private void Awake()
        {
            Model = new SalvageSpot(partDefinition);
            spriteRenderer = GetComponent<SpriteRenderer>();

            // Always (re)create at runtime, not just when null: a Sprite
            // assigned by editor-time setup code can fail to survive the
            // domain reload that happens on entering Play mode, which would
            // otherwise leave this renderer silently spriteless.
            var texture = Texture2D.whiteTexture;
            spriteRenderer.sprite = Sprite.Create(
                texture,
                new Rect(0, 0, texture.width, texture.height),
                new Vector2(0.5f, 0.5f),
                texture.width);

            Debug.Log($"[SalvageSpotView] {name} Awake: sprite assigned = {spriteRenderer.sprite != null}, part = {(partDefinition != null ? partDefinition.DisplayName : "null")}");
        }

        private void Update()
        {
            spriteRenderer.color = Model.State switch
            {
                SalvageSpotState.Available => AvailableColor,
                SalvageSpotState.Revealed => RevealedColor,
                _ => DepletedColor,
            };
        }
    }
}
