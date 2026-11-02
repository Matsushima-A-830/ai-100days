using System;

namespace SignalLost.Station
{
    /// <summary>
    /// Lifecycle states of a <see cref="RepairableSystem"/>. A system only ever
    /// moves forward: <see cref="Offline"/> -> <see cref="Repaired"/>.
    /// </summary>
    public enum RepairableSystemState
    {
        /// <summary>Not yet repaired; the default state at the start of a run.</summary>
        Offline,

        /// <summary>Repaired; nothing more can happen to this system.</summary>
        Repaired
    }

    /// <summary>
    /// A single named module aboard the <see cref="Station"/> (e.g. "Life Support")
    /// that starts <see cref="RepairableSystemState.Offline"/> and can be marked
    /// <see cref="RepairableSystemState.Repaired"/>. Plain, Unity-runtime-independent
    /// data object (no <see cref="UnityEngine.MonoBehaviour"/>), matching the pattern
    /// used by <c>SignalLost.Station.DecayTimer</c> and
    /// <c>SignalLost.Debris.SalvageSpot</c>, so it can be driven and unit-tested
    /// without the Unity runtime.
    ///
    /// All MVP systems behave identically (no unique per-system behaviour), so this
    /// is intentionally a single data-holding class rather than a subclass hierarchy.
    /// Spending a part to perform the repair (Story 006) and presenting the
    /// Offline/Repaired state in UI (Story 002) are out of scope here.
    /// </summary>
    public class RepairableSystem
    {
        /// <summary>The display name of this system (e.g. "Navigation").</summary>
        public string Name { get; }

        /// <summary>Current lifecycle state of this system.</summary>
        public RepairableSystemState State { get; private set; }

        /// <summary>True once this system has been repaired.</summary>
        public bool IsRepaired => State == RepairableSystemState.Repaired;

        /// <summary>
        /// Fires exactly once, the moment this system transitions from
        /// <see cref="RepairableSystemState.Offline"/> to
        /// <see cref="RepairableSystemState.Repaired"/>. Other systems (e.g. the
        /// win screen in Story 002, or the owning <see cref="Station"/>) subscribe
        /// to this to react to the repair.
        /// <code>
        /// system.Repaired += HandleSystemRepaired;
        /// </code>
        /// </summary>
        public event Action Repaired;

        /// <summary>
        /// Creates a new system, starting in the
        /// <see cref="RepairableSystemState.Offline"/> state.
        /// </summary>
        /// <param name="name">
        /// The display name of this system. Must not be null, empty, or
        /// whitespace.
        /// </param>
        public RepairableSystem(string name)
        {
            if (string.IsNullOrWhiteSpace(name))
            {
                throw new ArgumentException(
                    "System name must not be null or empty.",
                    nameof(name));
            }

            Name = name;
            State = RepairableSystemState.Offline;
        }

        /// <summary>
        /// Marks this system as repaired. Transitions
        /// <see cref="RepairableSystemState.Offline"/> to
        /// <see cref="RepairableSystemState.Repaired"/> and fires
        /// <see cref="Repaired"/>. Safe to call more than once: a system that is
        /// already <see cref="RepairableSystemState.Repaired"/> is left unchanged
        /// and <see cref="Repaired"/> does not fire again.
        /// </summary>
        /// <example>
        /// <code>
        /// // Story 006's repair action, after consuming the matching part.
        /// system.MarkRepaired();
        /// </code>
        /// </example>
        public void MarkRepaired()
        {
            if (State == RepairableSystemState.Repaired)
            {
                return;
            }

            State = RepairableSystemState.Repaired;
            Repaired?.Invoke();
        }
    }
}
