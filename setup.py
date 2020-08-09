import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ihd_usb_js_scrape",
    version="0.0.2",
    author="David Kent",
    author_email="davidkent@fastmail.com.au",
    description="Scrapes data from the USB mounted JS from an in home energy display",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dmkent/ihd-usb-js-scrape",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'calmjs.parse==1.2.5',
        'paho-mqtt==1.5.0',
        'pandas==1.1.0',
    ],
    entry_points = {
        'console_scripts': ['ihd_usb_js_scrape=ihd_usb_js_scrape:main'],
    },
    scripts=['bin/ihd_power_cycle_usb.sh'],
)
