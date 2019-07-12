#!/usr/bin/python
# Copyright 2016 The ANGLE Project Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# gen_vk_format_table.py:
#  Code generation for vk format map. See vk_format_map.json for data source.
#  NOTE: don't run this script directly. Run scripts/run_code_generation.py.

from datetime import date
import json
import math
import pprint
import os
import re
import sys

sys.path.append('..')
import angle_format

template_table_autogen_cpp = """// GENERATED FILE - DO NOT EDIT.
// Generated by {script_name} using data from {input_file_name}
//
// Copyright {copyright_year} The ANGLE Project Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
//
// {out_file_name}:
//   Queries for full Vulkan format information based on GL format.

#include "libANGLE/renderer/vulkan/vk_format_utils.h"

#include "image_util/copyimage.h"
#include "image_util/generatemip.h"
#include "image_util/loadimage.h"

using namespace angle;

namespace rx
{{

namespace vk
{{

void Format::initialize(RendererVk *renderer,
                        const angle::Format &angleFormat)
{{
    switch (angleFormat.id)
    {{
{format_case_data}
        default:
            UNREACHABLE();
            break;
    }}
}}

}}  // namespace vk

}}  // namespace rx
"""

empty_format_entry_template = """case angle::FormatID::{format_id}:
// This format is not implemented in Vulkan.
break;
"""

format_entry_template = """case angle::FormatID::{format_id}:
internalFormat = {internal_format};
{image_template}
{buffer_template}
break;
"""

image_basic_template = """imageFormatID = {image};
vkImageFormat = {vk_image_format};
imageInitializerFunction = {image_initializer};"""

image_struct_template = "{{{image}, {vk_image_format}, {image_initializer}}}"

image_fallback_template = """{{
static constexpr ImageFormatInitInfo kInfo[] = {{{image_list}}};
initImageFallback(renderer, kInfo, ArraySize(kInfo));
}}"""

buffer_basic_template = """bufferFormatID = {buffer};
vkBufferFormat = {vk_buffer_format};
vkBufferFormatIsPacked = {vk_buffer_format_is_packed};
vertexLoadFunction = {vertex_load_function};
vertexLoadRequiresConversion = {vertex_load_converts};"""

buffer_struct_template = """{{{buffer}, {vk_buffer_format}, {vk_buffer_format_is_packed}, 
{vertex_load_function}, {vertex_load_converts}}}"""

buffer_fallback_template = """{{
static constexpr BufferFormatInitInfo kInfo[] = {{{buffer_list}}};
initBufferFallback(renderer, kInfo, ArraySize(kInfo));
}}"""


def is_packed(format_id):
    return "true" if "_PACK" in format_id else "false"


def verify_vk_map_keys(angle_to_gl, vk_json_data):
    """Verify that the keys in Vulkan format tables exist in the ANGLE table.  If they don't, the
    entry in the Vulkan file is incorrect and needs to be fixed."""

    no_error = True
    for table in ["map", "overrides", "fallbacks"]:
        for angle_format in vk_json_data[table].keys():
            if not angle_format in angle_to_gl.keys():
                print "Invalid format " + angle_format + " in vk_format_map.json in " + table
                no_error = False

    return no_error


def gen_format_case(angle, internal_format, vk_json_data):
    vk_map = vk_json_data["map"]
    vk_overrides = vk_json_data["overrides"]
    vk_fallbacks = vk_json_data["fallbacks"]
    args = dict(
        format_id=angle, internal_format=internal_format, image_template="", buffer_template="")

    if ((angle not in vk_map) and (angle not in vk_overrides) and
        (angle not in vk_fallbacks)) or angle == 'NONE':
        return empty_format_entry_template.format(**args)

    def get_formats(format, type):
        format = vk_overrides.get(format, {}).get(type, format)
        if format not in vk_map:
            return []
        fallbacks = vk_fallbacks.get(format, {}).get(type, [])
        if not isinstance(fallbacks, list):
            fallbacks = [fallbacks]
        return [format] + fallbacks

    def image_args(format):
        return dict(
            image="angle::FormatID::" + format,
            vk_image_format=vk_map[format],
            image_initializer=angle_format.get_internal_format_initializer(
                internal_format, format))

    def buffer_args(format):
        return dict(
            buffer="angle::FormatID::" + format,
            vk_buffer_format=vk_map[format],
            vk_buffer_format_is_packed=is_packed(vk_map[format]),
            vertex_load_function=angle_format.get_vertex_copy_function(angle, format),
            vertex_load_converts='false' if angle == format else 'true',
        )

    images = get_formats(angle, "image")
    if len(images) == 1:
        args.update(image_template=image_basic_template)
        args.update(image_args(images[0]))
    elif len(images) > 1:
        args.update(
            image_template=image_fallback_template,
            image_list=", ".join(image_struct_template.format(**image_args(i)) for i in images))

    buffers = get_formats(angle, "buffer")
    if len(buffers) == 1:
        args.update(buffer_template=buffer_basic_template)
        args.update(buffer_args(buffers[0]))
    elif len(buffers) > 1:
        args.update(
            buffer_template=buffer_fallback_template,
            buffer_list=", ".join(
                buffer_struct_template.format(**buffer_args(i)) for i in buffers))

    return format_entry_template.format(**args).format(**args)


def main():

    input_file_name = 'vk_format_map.json'
    out_file_name = 'vk_format_table_autogen.cpp'

    # auto_script parameters.
    if len(sys.argv) > 1:
        inputs = ['../angle_format.py', '../angle_format_map.json', input_file_name]
        outputs = [out_file_name]

        if sys.argv[1] == 'inputs':
            print ','.join(inputs)
        elif sys.argv[1] == 'outputs':
            print ','.join(outputs)
        else:
            print('Invalid script parameters')
            return 1
        return 0

    angle_to_gl = angle_format.load_inverse_table(os.path.join('..', 'angle_format_map.json'))
    vk_json_data = angle_format.load_json(input_file_name)

    if not verify_vk_map_keys(angle_to_gl, vk_json_data):
        return 1

    vk_cases = [
        gen_format_case(angle, gl, vk_json_data) for angle, gl in sorted(angle_to_gl.iteritems())
    ]

    output_cpp = template_table_autogen_cpp.format(
        copyright_year=date.today().year,
        format_case_data="\n".join(vk_cases),
        script_name=__file__,
        out_file_name=out_file_name,
        input_file_name=input_file_name)

    with open(out_file_name, 'wt') as out_file:
        out_file.write(output_cpp)
        out_file.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
