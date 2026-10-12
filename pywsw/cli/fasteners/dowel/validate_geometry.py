import math

from .dowel_types import DowelInfo, DowelInputError


def _validate_lengths_single_shear(info: DowelInfo) -> DowelInfo:
    fastener, main, side, dowel = info

    # Adjust fastener lengths
    if math.isnan(fastener.length):
        fastener = fastener._replace(length=main.thickness + side.thickness)
    else:
        if info.fastener.length < info.main.thickness + info.side.thickness:
            main = main._replace(thickness=fastener.length - side.thickness)

    return DowelInfo(fastener, main, side, dowel)


def _validate_lengths_double_shear(info: DowelInfo) -> DowelInfo:
    fastener, main, side, dowel = info

    # Adjust fastener lengths
    if math.isnan(fastener.length):
        fastener = fastener._replace(length=main.thickness + 2 * side.thickness)
    else:
        grip = info.main.thickness + 2 * info.side.thickness
        if info.fastener.length < grip:
            raise DowelInputError(
                f"Fastener length {fastener.length:0.3f} is insufficient for {grip:0.3f} total grip."
            )

    return DowelInfo(fastener, main, side, dowel)


def validate_geometry(info: DowelInfo) -> DowelInfo:
    if info.fastener.double_shear:
        info = _validate_lengths_double_shear(info)
    else:
        info = _validate_lengths_single_shear(info)

    return info
