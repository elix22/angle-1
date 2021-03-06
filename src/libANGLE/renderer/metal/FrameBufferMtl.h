//
// Copyright 2019 The ANGLE Project Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
//
// FrameBufferMtl.h:
//    Defines the class interface for FrameBufferMtl, implementing FrameBufferImpl.
//

#ifndef LIBANGLE_RENDERER_METAL_FRAMEBUFFERMTL_H_
#define LIBANGLE_RENDERER_METAL_FRAMEBUFFERMTL_H_

#import <Metal/Metal.h>

#include "libANGLE/renderer/FramebufferImpl.h"

namespace rx
{

class FramebufferMtl : public FramebufferImpl
{
  public:
    explicit FramebufferMtl(const gl::FramebufferState &state);
    ~FramebufferMtl() override;
    void destroy(const gl::Context *context) override;

    angle::Result discard(const gl::Context *context,
                          size_t count,
                          const GLenum *attachments) override;
    angle::Result invalidate(const gl::Context *context,
                             size_t count,
                             const GLenum *attachments) override;
    angle::Result invalidateSub(const gl::Context *context,
                                size_t count,
                                const GLenum *attachments,
                                const gl::Rectangle &area) override;

    angle::Result clear(const gl::Context *context, GLbitfield mask) override;
    angle::Result clearBufferfv(const gl::Context *context,
                                GLenum buffer,
                                GLint drawbuffer,
                                const GLfloat *values) override;
    angle::Result clearBufferuiv(const gl::Context *context,
                                 GLenum buffer,
                                 GLint drawbuffer,
                                 const GLuint *values) override;
    angle::Result clearBufferiv(const gl::Context *context,
                                GLenum buffer,
                                GLint drawbuffer,
                                const GLint *values) override;
    angle::Result clearBufferfi(const gl::Context *context,
                                GLenum buffer,
                                GLint drawbuffer,
                                GLfloat depth,
                                GLint stencil) override;

    GLenum getImplementationColorReadFormat(const gl::Context *context) const override;
    GLenum getImplementationColorReadType(const gl::Context *context) const override;
    angle::Result readPixels(const gl::Context *context,
                             const gl::Rectangle &area,
                             GLenum format,
                             GLenum type,
                             void *pixels) override;

    angle::Result blit(const gl::Context *context,
                       const gl::Rectangle &sourceArea,
                       const gl::Rectangle &destArea,
                       GLbitfield mask,
                       GLenum filter) override;

    bool checkStatus(const gl::Context *context) const override;

    angle::Result syncState(const gl::Context *context,
                            const gl::Framebuffer::DirtyBits &dirtyBits) override;

    angle::Result getSamplePosition(const gl::Context *context,
                                    size_t index,
                                    GLfloat *xy) const override;
};
}  // namespace rx

#endif /* LIBANGLE_RENDERER_METAL_FRAMEBUFFERMTL_H */
