# VanLAN Apt Repository

To use this repository:

```bash
curl -s https://andyphelps.github.io/vanlan/public.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/vanlan.gpg > /dev/null
echo "deb https://andyphelps.github.io/vanlan/ trixie main" | sudo tee /etc/apt/sources.list.d/vanlan.list
sudo apt update
sudo apt install vanlan-router
```
