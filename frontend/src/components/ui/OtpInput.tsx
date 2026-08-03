import React, { useRef, useState, useEffect } from "react"

interface OtpInputProps {
  length?: number
  onComplete: (code: string) => void
  isDisabled?: boolean
}

export function OtpInput({ length = 6, onComplete, isDisabled = false }: OtpInputProps) {
  const [otp, setOtp] = useState<string[]>(Array(length).fill(""))
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  useEffect(() => {
    // Focus first input on mount
    if (inputRefs.current[0] && !isDisabled) {
      inputRefs.current[0].focus()
    }
  }, [isDisabled])

  const handleChange = (index: number, value: string) => {
    if (isDisabled) return
    const digit = value.slice(-1)
    if (!/^\d*$/.test(digit)) return

    const newOtp = [...otp]
    newOtp[index] = digit
    setOtp(newOtp)

    // Move to next input box if filled
    if (digit && index < length - 1) {
      inputRefs.current[index + 1]?.focus()
    }

    // Call onComplete if all digits filled
    const fullCode = newOtp.join("")
    if (fullCode.length === length && !newOtp.includes("")) {
      onComplete(fullCode)
    }
  }

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (isDisabled) return

    if (e.key === "Backspace") {
      if (!otp[index] && index > 0) {
        inputRefs.current[index - 1]?.focus()
      }
    }
  }

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    if (isDisabled) return
    e.preventDefault()
    const pastedData = e.clipboardData.getData("text").trim()
    if (!/^\d+$/.test(pastedData)) return

    const digits = pastedData.slice(0, length).split("")
    const newOtp = [...otp]
    digits.forEach((d, i) => {
      newOtp[i] = d
    })
    setOtp(newOtp)

    const nextIndex = Math.min(digits.length, length - 1)
    inputRefs.current[nextIndex]?.focus()

    const fullCode = newOtp.join("")
    if (fullCode.length === length && !newOtp.includes("")) {
      onComplete(fullCode)
    }
  }

  return (
    <div className="flex justify-center items-center gap-2 sm:gap-3">
      {otp.map((digit, idx) => (
        <input
          key={idx}
          ref={(el) => (inputRefs.current[idx] = el)}
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={1}
          value={digit}
          disabled={isDisabled}
          onChange={(e) => handleChange(idx, e.target.value)}
          onKeyDown={(e) => handleKeyDown(idx, e)}
          onPaste={handlePaste}
          className="w-10 h-12 sm:w-12 sm:h-14 rounded-2xl border-2 border-input bg-background/80 text-center text-lg sm:text-xl font-bold text-foreground focus:border-primary focus:ring-4 focus:ring-primary/20 transition-all outline-hidden disabled:opacity-50"
        />
      ))}
    </div>
  )
}
