echo "--------------------------------------------"
echo "Uninstalling Stream Processing Platform"
echo "--------------------------------------------"
echo "--------------------------------------------"
echo "Stopping Instancemanager"
echo "--------------------------------------------"
systemctl stop instancemanager.service
systemctl disable instancemanager.service
rm -r /etc/systemd/system/instancemanager.service
echo "--------------------------------------------"
echo "Stopping Converter"
echo "--------------------------------------------"
systemctl stop converter.service
systemctl disable converter.service
rm -r /etc/systemd/system/converter.service
rm -r /opt/Stream-Processing/
echo "--------------------------------------------"
echo "Stopping NodeRED"
echo "--------------------------------------------"
kubectl delete namespace gui
echo "--------------------------------------------"
echo "Stopping KEDA"
echo "--------------------------------------------"
kubectl delete namespace keda
echo "--------------------------------------------"
echo "Stopping RabbitMQ"
echo "--------------------------------------------"
kubectl delete namespace rabbit