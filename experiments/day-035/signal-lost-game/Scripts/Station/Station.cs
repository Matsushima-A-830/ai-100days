using System;
using System.Collections.Generic;
using System.Linq;

namespace SignalLost.Station
{
    /// <summary>
    /// The single station layout for the MVP: a fixed set of named
    /// <see cref="RepairableSystem"/> modules, each starting
    /// <see cref="RepairableSystemState.Offline"/>. Plain, Unity-runtime-independent
    /// container (no <see cref="UnityEngine.MonoBehaviour"/>), matching the pattern
    /// used by <c>SignalLost.Debris.DebrisField</c>.
    ///
    /// Per the brief's out-of-scope list there is exactly one layout for the MVP —
    /// the set of systems is constructed directly here rather than taking a
    /// configurable list.
    /// </summary>
    public class Station
    {
        /// <summary>
        /// The systems aboard this station, in construction order. Fixed for the
        /// lifetime of the <see cref="Station"/> instance.
        /// </summary>
        public IReadOnlyList<RepairableSystem> Systems { get; }

        /// <summary>
        /// True once every system in <see cref="Systems"/> has been repaired.
        /// Computed live from current system state (safe to read at any time,
        /// not just after <see cref="AllRepaired"/> fires).
        /// </summary>
        public bool AllSystemsRepaired => Systems.All(s => s.IsRepaired);

        /// <summary>
        /// Fires exactly once, the moment the last Offline system transitions to
        /// Repaired (i.e. the tick <see cref="AllSystemsRepaired"/> first becomes
        /// true). Story 002's win screen subscribes to this.
        /// <code>
        /// station.AllRepaired += HandleStationRepaired;
        /// </code>
        /// </summary>
        public event Action AllRepaired;

        private bool hasFiredAllRepaired;

        /// <summary>
        /// Creates the station with its fixed set of four systems: Life Support,
        /// Navigation, Power Core, and Comms. All start
        /// <see cref="RepairableSystemState.Offline"/>.
        /// </summary>
        public Station()
        {
            Systems = new List<RepairableSystem>
            {
                new RepairableSystem("Life Support"),
                new RepairableSystem("Navigation"),
                new RepairableSystem("Power Core"),
                new RepairableSystem("Comms")
            };

            foreach (var system in Systems)
            {
                system.Repaired += HandleSystemRepaired;
            }
        }

        private void HandleSystemRepaired()
        {
            if (hasFiredAllRepaired || !AllSystemsRepaired)
            {
                return;
            }

            hasFiredAllRepaired = true;
            AllRepaired?.Invoke();
        }
    }
}
