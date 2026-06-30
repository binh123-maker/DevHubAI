import { useParams } from "react-router-dom"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function DocumentViewerPage() {
  const { id } = useParams()

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Document Viewer</h1>
      <Card>
        <CardHeader>
          <CardTitle>Document ID: {id}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Trình xem tài liệu sẽ được triển khai sau.</p>
        </CardContent>
      </Card>
    </div>
  )
}
