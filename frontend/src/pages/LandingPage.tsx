import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function LandingPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/20 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>DevHub AI</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            Nền tảng quản lý tri thức và trò chuyện AI cho nhóm phát triển — MVP-8W scaffold.
          </p>
          <div className="flex gap-3">
            <Button asChild>
              <Link to="/login">Đăng nhập</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/register">Đăng ký</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
