# LineageOS 17.1 for the Galaxy Tab A 7.0 (SM-T280)

Community Android 10 port for the Wi-Fi SM-T280 (`gtexswifi`, ARMv7). This repository provides the pinned Android source manifest, 12 project patches, and instructions for building the source baseline used for R2.

## Build the source baseline

The recorded build used an x86-64 Linux host, Git, Git LFS, Google's [Repo tool](https://source.android.com/docs/setup/download), GCC multilib, ccache, Python 2 and Python 3. Keep the source checkout and legacy toolchain in paths without spaces. The initial checkout occupied about 67 GiB before build outputs. Allow additional space for compilation.

Clone this repository and use it as the Repo manifest. The manifest fetches device dependencies from their upstream repositories, including the vendor source tree. Install the Android build host dependencies and initialize Git LFS before syncing.

```sh
git lfs install
git clone https://github.com/jolie1204/lineageos-17.1-gtexswifi.git port
mkdir lineage-17.1
cd lineage-17.1
repo init -u https://github.com/jolie1204/lineageos-17.1-gtexswifi.git -b main
repo sync -j4
python3 ../port/apply-patches.py . --apply
```

The patch script checks all project commits and checksums before it stages any changes. Omit `--apply` to validate patches against the pinned commits using temporary Git indexes. Use a fresh source checkout for application.

Install the pinned ARM EABI GCC 4.8 toolchain. The environment variable points to the directory containing its `bin/` subdirectory.

```sh
git clone https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-eabi-4.8 ../arm-eabi-4.8
git -C ../arm-eabi-4.8 checkout --detach 26e93f6af47f7bd3a9beb5c102a5f45e19bfa38a
export GTEXSWIFI_KERNEL_TOOLCHAIN="$(cd ../arm-eabi-4.8 && pwd)"
test -x "$GTEXSWIFI_KERNEL_TOOLCHAIN/bin/arm-eabi-gcc"
```

The original build put a `python` shim pointing to Python 2 ahead of the system PATH for legacy build steps. On hosts where `python` does not resolve to Python 2, add such a shim for this build shell after Repo sync. Then build from the Android tree.

```sh
source build/envsetup.sh
lunch lineage_gtexswifi-userdebug
m -j8 systemimage ramdisk
```

The source targets produce build outputs under `out/target/product/gtexswifi/`. The locally tested R2 package used additional device-specific boot packaging, a Google services layer, and matching system and vendor build fingerprints. This repository distributes the source baseline only. A new build requires its own packaging and boot validation.

## Validation on SM-T280

- The locally assembled R2 system booted after a data-preserving install. The user confirmed display, touch, YouTube video and playback audio.
- The camera changes were tested with physical front and rear preview, switching cameras, reopening the app and rear preview after reboot. Front and rear JPEG save and gallery reopen passed. Video recording coverage was rear QVGA H.264/AAC.
- The build uses permissive SELinux. Fresh-userdata installation, Odin transport and long-duration stability were outside the reported R2 validation.

## Credits and licensing

- [YIRMELSANCHEZ's Android 10 port](https://github.com/YIRMELSANCHEZ/porting-galaxy-tab-a/tree/94ef29b62c46e58e6c9088bf8fd110652d0e58e7) supplied the reference manifest and earlier porting work. Its attribution and MIT notice are preserved in [licenses/port-reference-MIT.txt](licenses/port-reference-MIT.txt).
- [_mone's SM-T280 device tree](https://github.com/underscoremone/android_device_samsung_gtexswifi) and [kernel](https://github.com/underscoremone/android_kernel_samsung_gtexswifi) provided the device baseline. The pinned manifest also credits the Spreadtrum hardware and Samsung vendor repositories.
- [LineageOS](https://github.com/LineageOS) and the [Android Open Source Project](https://source.android.com/) provided the Android platform. Patches retain the copyright notices and license terms of their source files. The [kernel COPYING file](licenses/kernel-COPYING.txt) and [Apache 2.0 text](licenses/Apache-2.0.txt) are included for reference. Refer to the pinned upstream projects for component-specific terms.
