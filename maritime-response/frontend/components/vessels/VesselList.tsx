import { Vessel } from "@/types/vessel";
import VesselCard from "./VesselCard";

interface Props {
  vessels: Vessel[];
}

export default function VesselList({ vessels }: Props) {
  if (vessels.length === 0) {
    return (
      <div className="rounded-xl border border-dashed p-8 text-center text-gray-500">
        No vessels found.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {vessels.map((vessel) => (
        <VesselCard
          key={vessel.id}
          vessel={vessel}
        />
      ))}
    </div>
  );
}