def verification_email(otp: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Verify your Marketcore account</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:Inter,Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
    <tr>
      <td align="center" style="padding:48px 16px;">
        <table width="560" cellpadding="0" cellspacing="0" role="presentation"
               style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08);">
          <tr>
            <td style="background:#6d28d9;padding:32px 40px;">
              <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;letter-spacing:-.3px;">
                Marketcore
              </h1>
            </td>
          </tr>
          <tr>
            <td style="padding:40px;">
              <h2 style="margin:0 0 16px;color:#111827;font-size:20px;font-weight:600;">
                Verify your email address
              </h2>
              <p style="margin:0 0 24px;color:#6b7280;font-size:15px;line-height:1.6;">
                Thanks for signing up! Use the code below to confirm your address.
                It expires in <strong>10 minutes</strong>.
              </p>
              <div style="margin:0 0 24px;padding:24px;background:#f5f3ff;border-radius:8px;text-align:center;">
                <span style="font-size:40px;font-weight:800;letter-spacing:12px;color:#6d28d9;">
                  {otp}
                </span>
              </div>
              <p style="margin:0;color:#9ca3af;font-size:13px;">
                If you didn't create an account, you can safely ignore this email.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 40px;border-top:1px solid #f3f4f6;">
              <p style="margin:0;color:#d1d5db;font-size:12px;">
                &copy; 2026 Marketcore. All rights reserved.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def welcome_email(email: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Welcome to Marketcore</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:Inter,Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
    <tr>
      <td align="center" style="padding:48px 16px;">
        <table width="560" cellpadding="0" cellspacing="0" role="presentation"
               style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08);">
          <tr>
            <td style="background:#6d28d9;padding:32px 40px;">
              <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;letter-spacing:-.3px;">
                Marketcore
              </h1>
            </td>
          </tr>
          <tr>
            <td style="padding:40px;">
              <h2 style="margin:0 0 16px;color:#111827;font-size:20px;font-weight:600;">
                Welcome aboard!
              </h2>
              <p style="margin:0 0 16px;color:#6b7280;font-size:15px;line-height:1.6;">
                Your email <strong>{email}</strong> is now verified. You're all set to start buying
                and selling on Marketcore.
              </p>
              <p style="margin:0 0 32px;color:#6b7280;font-size:15px;line-height:1.6;">
                Explore thousands of products, manage your listings, and track your orders — all in one place.
              </p>
              <a href="https://marketcore.io"
                 style="display:inline-block;padding:14px 28px;background:#6d28d9;color:#ffffff;
                        text-decoration:none;border-radius:6px;font-size:15px;font-weight:600;">
                Go to Marketcore
              </a>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 40px;border-top:1px solid #f3f4f6;">
              <p style="margin:0;color:#d1d5db;font-size:12px;">
                &copy; 2026 Marketcore. All rights reserved.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def payment_confirmed_email(order_id: str, amount: float, currency: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8" /><title>Payment confirmed</title></head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:Inter,Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
    <tr>
      <td align="center" style="padding:48px 16px;">
        <table width="560" cellpadding="0" cellspacing="0" role="presentation"
               style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08);">
          <tr>
            <td style="background:#6d28d9;padding:32px 40px;">
              <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;">Marketcore</h1>
            </td>
          </tr>
          <tr>
            <td style="padding:40px;">
              <h2 style="margin:0 0 16px;color:#111827;font-size:20px;font-weight:600;">
                Payment confirmed ✓
              </h2>
              <p style="margin:0 0 8px;color:#6b7280;font-size:15px;line-height:1.6;">
                Your payment for order <strong>{order_id}</strong> was successful.
              </p>
              <p style="margin:0;color:#111827;font-size:22px;font-weight:700;">
                {currency} {amount:.2f}
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 40px;border-top:1px solid #f3f4f6;">
              <p style="margin:0;color:#d1d5db;font-size:12px;">&copy; 2026 Marketcore.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def payment_failed_email(order_id: str, reason: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8" /><title>Payment failed</title></head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:Inter,Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
    <tr>
      <td align="center" style="padding:48px 16px;">
        <table width="560" cellpadding="0" cellspacing="0" role="presentation"
               style="background:#ffffff;border-radius:8px;overflow:hidden;">
          <tr>
            <td style="background:#6d28d9;padding:32px 40px;">
              <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;">Marketcore</h1>
            </td>
          </tr>
          <tr>
            <td style="padding:40px;">
              <h2 style="margin:0 0 16px;color:#dc2626;font-size:20px;font-weight:600;">
                Payment failed
              </h2>
              <p style="margin:0 0 8px;color:#6b7280;font-size:15px;line-height:1.6;">
                We couldn't process your payment for order <strong>{order_id}</strong>.
              </p>
              <p style="margin:0;color:#6b7280;font-size:14px;">Reason: {reason}</p>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 40px;border-top:1px solid #f3f4f6;">
              <p style="margin:0;color:#d1d5db;font-size:12px;">&copy; 2026 Marketcore.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def product_published_email(product_name: str, product_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8" /><title>Your product is live</title></head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:Inter,Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
    <tr>
      <td align="center" style="padding:48px 16px;">
        <table width="560" cellpadding="0" cellspacing="0" role="presentation"
               style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08);">
          <tr>
            <td style="background:#6d28d9;padding:32px 40px;">
              <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;letter-spacing:-.3px;">
                Marketcore
              </h1>
            </td>
          </tr>
          <tr>
            <td style="padding:40px;">
              <h2 style="margin:0 0 16px;color:#111827;font-size:20px;font-weight:600;">
                Your product is live!
              </h2>
              <p style="margin:0 0 24px;color:#6b7280;font-size:15px;line-height:1.6;">
                <strong>{product_name}</strong> has been processed and is now visible to buyers on Marketcore.
              </p>
              <a href="https://marketcore.io/products/{product_id}"
                 style="display:inline-block;padding:14px 28px;background:#6d28d9;color:#ffffff;
                        text-decoration:none;border-radius:6px;font-size:15px;font-weight:600;">
                View your listing
              </a>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 40px;border-top:1px solid #f3f4f6;">
              <p style="margin:0;color:#d1d5db;font-size:12px;">&copy; 2026 Marketcore. All rights reserved.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


__all__ = [
    "verification_email",
    "welcome_email",
    "payment_confirmed_email",
    "payment_failed_email",
    "product_published_email",
]
