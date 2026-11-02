using System.Collections.Generic;

namespace SignalLost.Debris
{
    /// <summary>
    /// A collection of <see cref="SalvageSpot"/>s the player can scan and collect
    /// parts from. Plain, Unity-runtime-independent container (no
    /// <see cref="UnityEngine.MonoBehaviour"/>), matching the pattern used by
    /// <c>SignalLost.Station.DecayTimer</c>. Holds no enemy/hazard state — the brief
    /// explicitly excludes those from the debris field.
    /// </summary>
    public class DebrisField
    {
        private readonly List<SalvageSpot> salvageSpots;

        /// <summary>
        /// The salvage spots in this field, in the order they were supplied to the
        /// constructor. Read-only: spots are added only at construction time.
        /// </summary>
        public IReadOnlyList<SalvageSpot> SalvageSpots => salvageSpots;

        /// <summary>
        /// Creates a debris field containing the given salvage spots.
        /// </summary>
        /// <param name="salvageSpots">
        /// One or more spots to populate the field with. Copied into an internal
        /// list, so later changes to the caller's collection do not affect this field.
        /// </param>
        public DebrisField(IEnumerable<SalvageSpot> salvageSpots)
        {
            this.salvageSpots = new List<SalvageSpot>(salvageSpots);
        }
    }
}
