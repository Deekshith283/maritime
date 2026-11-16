import { Card, CardContent } from "@/components/ui/card";

interface Props {
  title: string;
  value: string;
}

export default function DashboardCard({
  title,
  value,
}: Props) {
  return (
    <Card>
      <CardContent className="p-6">
        <p className="text-muted-foreground">
          {title}
        </p>

        <h2 className="mt-2 text-3xl font-bold">
          {value}
        </h2>
      </CardContent>
    </Card>
  );
}
