/*
 * Copyright 2023 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

/***********************************************************************************/
/* This file is automatically generated using bindtool and can be manually edited  */
/* The following lines can be configured to regenerate this file during cmake      */
/* If manual edits are made, the following tags should be modified accordingly.    */
/* BINDTOOL_GEN_AUTOMATIC(0)                                                       */
/* BINDTOOL_USE_PYGCCXML(0)                                                        */
/* BINDTOOL_HEADER_FILE(gnugym_snrdebug_ff.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(add18a402394cb154832b5b943f0f4cd)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <gnugym/gnugym_snrdebug_ff.h>
// pydoc.h is automatically generated in the build directory
#include <gnugym_snrdebug_ff_pydoc.h>

void bind_gnugym_snrdebug_ff(py::module& m)
{

    using gnugym_snrdebug_ff    = ::gr::gnugym::gnugym_snrdebug_ff;


    py::class_<gnugym_snrdebug_ff, gr::block, gr::basic_block,
        std::shared_ptr<gnugym_snrdebug_ff>>(m, "gnugym_snrdebug_ff", D(gnugym_snrdebug_ff))

        .def(py::init(&gnugym_snrdebug_ff::make),
           D(gnugym_snrdebug_ff,make)
        )
        



        ;




}







