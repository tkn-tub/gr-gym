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
/* BINDTOOL_HEADER_FILE(gnugym_parse_seqnr.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(b2b72d7b9b370e2ab954c87a48ac6fa7)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <gnuradio/gnugym/gnugym_parse_seqnr.h>
// pydoc.h is automatically generated in the build directory
#include <gnugym_parse_seqnr_pydoc.h>

void bind_gnugym_parse_seqnr(py::module& m)
{

    using gnugym_parse_seqnr    = gr::gnugym::gnugym_parse_seqnr;


    py::class_<gnugym_parse_seqnr, gr::block, gr::basic_block,
        std::shared_ptr<gnugym_parse_seqnr>>(m, "gnugym_parse_seqnr", D(gnugym_parse_seqnr))

        .def(py::init(&gnugym_parse_seqnr::make),
           D(gnugym_parse_seqnr,make)
        )
        



        ;




}








