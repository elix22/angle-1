//
// Copyright 2016 The ANGLE Project Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
//
// 20190119 - Eli Aloni (A.K.A. elix22)  - initial creation , MoltenVK support
//
// DisplayVkiOS.h:
//    Defines the class interface for DisplayVkiOS, implementing DisplayVk for iOS.
//


#ifndef LIBANGLE_RENDERER_VULKAN_IOS_DISPLAYVKMACOS_H_
#define LIBANGLE_RENDERER_VULKAN_IOS_DISPLAYVKMACOS_H_

#include "libANGLE/renderer/vulkan/DisplayVk.h"

namespace rx
{
class DisplayVkiOS : public DisplayVk
{
  public:
    DisplayVkiOS(const egl::DisplayState &state);

    bool isValidNativeWindow(EGLNativeWindowType window) const override;

    SurfaceImpl *createWindowSurfaceVk(const egl::SurfaceState &state,
                                       EGLNativeWindowType window,
                                       EGLint width,
                                       EGLint height) override;

    egl::ConfigSet generateConfigs() override;
    bool checkConfigSupport(egl::Config *config) override;

    const char *getWSIName() const override;
};

}  // namespace rx

#endif  // LIBANGLE_RENDERER_VULKAN_IOS_DISPLAYVKMACOS_H_
