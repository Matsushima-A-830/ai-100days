using UnityEngine;

namespace SignalLost.Debris
{
    /// <summary>
    /// Data-driven definition of a salvageable part. Authored as an asset in the
    /// editor (via the Create menu below) rather than hardcoded, so designers can
    /// add or tune parts without touching code. Referenced by <see cref="SalvageSpot"/>;
    /// what happens to the part once collected (hauling it, repairing a system with
    /// it) is handled by later stories, not here.
    /// </summary>
    [CreateAssetMenu(fileName = "NewPartDefinition", menuName = "SignalLost/Debris/Part Definition")]
    public class PartDefinition : ScriptableObject
    {
        [SerializeField]
        private string partId;

        [SerializeField]
        private string displayName;

        [SerializeField]
        private string targetSystemName;

        /// <summary>
        /// Stable identifier for this part, independent of its display name or
        /// asset file name. Intended for save data and lookups.
        /// </summary>
        public string PartId => partId;

        /// <summary>
        /// Human-readable name shown to the player (e.g. in a HUD prompt).
        /// </summary>
        public string DisplayName => displayName;

        /// <summary>
        /// The exact <see cref="SignalLost.Station.RepairableSystem.Name"/> this
        /// part repairs. Parts map 1:1 to systems — no crafting or combining —
        /// so this is a single string, not a list. Used by Story 006's
        /// <see cref="SignalLost.Station.RepairAction"/> to find the held part
        /// matching a given system.
        /// </summary>
        public string TargetSystemName => targetSystemName;
    }
}
